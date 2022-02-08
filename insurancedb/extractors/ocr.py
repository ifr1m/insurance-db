import logging
import re
from dataclasses import dataclass

import cv2 as cv
import numpy as np

import pdfplumber

from insurancedb.extractors.base import BaseRcaExtractor
from insurancedb.extractors.registry import extractor_register
from insurancedb.extractors.extractor_methods import get_pdf_page_image, get_image_text_using_ocr, get_image_digits_using_ocr, \
    get_ro_car_number_from_image, remove_slashes, is_RCA, clean_text, get_date, get_car_number, \
    find_position_of_template, to_opencv
from insurancedb.utils import get_project_root

resources_dir = get_project_root() / "resources"


@dataclass
@extractor_register
class AxeriaRcaExtractor(BaseRcaExtractor):
    pdf: pdfplumber.PDF = None

    def __post_init__(self):
        self.logger = logging.getLogger(f'{__name__}.{self.__class__.__name__}')
        empty = ""
        self.contract_name_l = empty
        self.insurer_name_l = empty
        self.insurance_number_l = empty
        self.amount_class_l = empty
        self.start_end_l = empty
        self.person_name_l = empty
        self.car_number_l = empty
        self.is_matching = False

        pages = [2]
        for page in pages:
            page_img = get_pdf_page_image(self.pdf, page)
            if page_img is not None:
                self.contract_name_l = get_image_text_using_ocr(page_img.crop((140, 3631, 2931, 3730)))
                self.insurer_name_l = get_image_text_using_ocr(page_img.crop((140, 3917, 2011, 4005)))
                self.is_matching = self._is_match()
                if self.is_matching:
                    self._continue_extracting(page_img)
                    self._log_extracted_values()
                    break

    def _continue_extracting(self, page_img):
        self.insurance_number_l = get_image_digits_using_ocr(page_img.crop((1598, 1111, 2761, 1325)))
        self.start_end_l = get_image_text_using_ocr(page_img.crop((130, 5682, 4814, 5810)))
        self.amount_class_l = get_image_text_using_ocr(page_img.crop((130, 5808, 4814, 5930)))
        self.person_name_l = get_image_text_using_ocr(page_img.crop((1064, 4397, 2685, 4547)))
        self.car_number_l = get_ro_car_number_from_image(page_img.crop((183, 1478, 1572, 1635)))
        self.insurance_number_l = remove_slashes(self.insurance_number_l)

    def _log_extracted_values(self):
        self.logger.debug(
            "contract_name_p: %s, insurer_name_p: %s, insurance_number_p: %s, start_end_p: %s, amount_class_p: %s, person_name_p: %s, car_number_p: %s",
            self.contract_name_l, self.insurer_name_l, self.insurance_number_l, self.start_end_l, self.amount_class_l,
            self.person_name_l, self.car_number_l)

    def is_match(self):
        return self.is_matching

    def _is_match(self):
        is_rca = is_RCA(self.contract_name_l)
        return is_rca and self.get_insurer_name() == "AXERIA IARD"

    def get_insurer_short_name(self):
        return "AXERIA"

    def get_insurer_name(self):
        match = re.search(r'(.*)SA LYON — SUCURSALA BUCURESTI', self.insurer_name_l)
        if match:
            return clean_text(match.group(1))
        else:
            return None

    def get_insurance_number(self):

        match = re.search(r'([\s\d]*)', self.insurance_number_l)
        if match:
            txt = match.group(1).strip()
            txt = re.sub(r'\s', "", txt)
            return txt
        else:
            return None

    def get_insurance_class(self):
        match = re.search(r'Clasa\s*Bonus\s*Malus(.*)Tarif', self.amount_class_l)
        if match:
            return clean_text(match.group(1))
        else:
            return None

    def get_start_date(self):
        return get_date(self.start_end_l, r'Contract\s*de\s*la(.*)\.(.*)\.(.*)până')

    def get_expiration_date(self):
        return get_date(self.start_end_l, r'până\s*la:(.*)\.(.*)\.(.*)Contract emis')

    def get_contract_date(self):
        return get_date(self.start_end_l, r'Contract\s*emis\s*în\s*data:(.*)\.(.*)\.(.*)\s(.*):(.*)')

    def get_person_name(self):
        return clean_text(self.person_name_l)

    def get_car_number(self):
        return get_car_number(self.car_number_l)

    def get_insurance_amount(self):
        match = re.search(r'Prima\s*de\s*asigurare(.*)Lei Clasa', self.amount_class_l)
        if match:
            return clean_text(match.group(1))
        else:
            return None


@dataclass
@extractor_register
class AllianzRcaExtractor(BaseRcaExtractor):
    pdf: pdfplumber.PDF = None

    def __post_init__(self):
        self.logger = logging.getLogger(f'{__name__}.{self.__class__.__name__}')
        self.anchors = {"page-top-left": (0, 0)}

        empty = ""
        self.contract_name_l = empty
        self.insurer_name_l = empty
        self.insurance_number_l = empty
        self.amount_class_l = empty
        self.start_end_l = empty
        self.person_name_l = empty
        self.car_number_l = empty
        self.is_matching = False

        pages = [0, 2]
        for page in pages:
            page_img = get_pdf_page_image(self.pdf, page)
            if page_img is not None:
                insurer_nm_bbox = find_position_of_template(to_opencv(page_img), cv.imread(
                    str(resources_dir / "insurer_nm_allianz.png")))
                if not insurer_nm_bbox.empty:
                    self.anchors["insurer-nm-allianz"] = (insurer_nm_bbox.iloc[0][0], insurer_nm_bbox.iloc[0][1])
                    crop_points_dict = self._get_crop_points_dict()
                    self.contract_name_l = get_image_text_using_ocr(page_img.crop(crop_points_dict["contract_name_l"]))  #
                    self.insurer_name_l = get_image_text_using_ocr(page_img.crop(crop_points_dict["insurer_name_l"]))
                    self.is_matching = self._is_match()
                    if self.is_matching:
                        self._continue_extracting(page_img, crop_points_dict)
                        self._log_extracted_values()
                        break

    def _get_crop_points_dict(self):
        relative_crop_points = np.array([[-4, -100, 2712, 10],  # contract_name_l / insurer-nm-allianz
                                         [0, 0, 2254, 118],  # insurer_name_l /  insurer-nm-allianz
                                         [1582, 1186, 2773, 1344],  # insurance_number_p / page-top-left
                                         [-6, 1580, 4786, 1704],  # amount_class_l /  insurer-nm-allianz
                                         [-6, 1470, 4786, 1578],  # start_end_l /  insurer-nm-allianz
                                         [1092, 324, 2636, 510],  # person_name_l /  insurer-nm-allianz
                                         [180, 1600, 1566, 1756]  # car_number_l /  page-top-left
                                         ])
        anchors_array = ["insurer-nm-allianz", "insurer-nm-allianz", "page-top-left", "insurer-nm-allianz",
                         "insurer-nm-allianz", "insurer-nm-allianz", "page-top-left"]
        anchors_array = [list(self.anchors[a]) for a in anchors_array]
        anchors_array = np.array(anchors_array)
        anchors_array = np.concatenate((anchors_array, anchors_array), axis=1)

        crop_points = anchors_array + relative_crop_points

        crop_points_names = ["contract_name_l", "insurer_name_l", "insurance_number_l", "amount_class_l", "start_end_l",
                             "person_name_l", "car_number_l"]

        result = {}
        for np_row, name in zip(crop_points, crop_points_names):
            result[name] = tuple(np_row)

        return result

    def _continue_extracting(self, page_img, crop_points_dict):
        self.insurance_number_l = get_image_digits_using_ocr(page_img.crop(crop_points_dict["insurance_number_l"]))
        self.amount_class_l = get_image_text_using_ocr(page_img.crop(crop_points_dict["amount_class_l"]))  #
        self.start_end_l = get_image_text_using_ocr(page_img.crop(crop_points_dict["start_end_l"]))  #
        self.person_name_l = get_image_text_using_ocr(page_img.crop(crop_points_dict["person_name_l"]))  #
        self.car_number_l = get_ro_car_number_from_image(page_img.crop(crop_points_dict["car_number_l"]))
        self.insurance_number_l = remove_slashes(self.insurance_number_l)

    def _log_extracted_values(self):
        self.logger.debug(
            "contract_name_p: %s, insurer_name_p: %s, insurance_number_p: %s, start_end_p: %s, amount_class_p: %s, person_name_p: %s, car_number_p: %s",
            self.contract_name_l, self.insurer_name_l, self.insurance_number_l, self.start_end_l, self.amount_class_l,
            self.person_name_l, self.car_number_l)

    def is_match(self):
        return self.is_matching

    def _is_match(self):
        is_rca = is_RCA(self.contract_name_l)
        return is_rca and self.get_insurer_name() == "ALLIANZ - ŢIRIAC ASIGURĂRI"

    def get_insurer_short_name(self):
        return "ALLIANZ"

    def get_insurer_name(self):
        match = re.search(r'Denumire asigurator:(.*)S\.A\.', self.insurer_name_l)
        if match:
            return clean_text(match.group(1))
        else:
            return None

    def get_insurance_number(self):

        match = re.search(r'([\s\d]*)', self.insurance_number_l)
        if match:
            txt = match.group(1).strip()
            txt = re.sub(r'\s', "", txt)
            return txt
        else:
            return None

    def get_insurance_class(self):
        match = re.search(r'Clasa Bonus Malus(.*)Tarif decontare', self.amount_class_l)
        if match:
            return clean_text(match.group(1))
        else:
            return None

    def get_start_date(self):
        return get_date(self.start_end_l, r'Valabilitate Contract de la(.*)\.(.*)\.(.*)până')

    def get_expiration_date(self):
        return get_date(self.start_end_l, r'la:(.*)\.(.*)\.(.*)Contract emis')

    def get_contract_date(self):
        return get_date(self.start_end_l, r'Contract emis în data(.*)\.(.*)\.(.*)')

    def get_person_name(self):
        return clean_text(self.person_name_l)

    def get_car_number(self):
        return get_car_number(self.car_number_l)

    def get_insurance_amount(self):
        match = re.search(r'Prima de asigurare(.*)(RO0N|RON|R0N) Clasa Bonus', self.amount_class_l)
        if match:
            return clean_text(match.group(1))
        else:
            return None


@dataclass
@extractor_register
class GroupamaRcaExtractor(BaseRcaExtractor):
    pdf: pdfplumber.PDF = None

    def __post_init__(self):
        self.logger = logging.getLogger(f'{__name__}.{self.__class__.__name__}')
        empty = ""
        self.contract_name_l = empty
        self.insurer_name_l = empty
        self.insurance_number_l = empty
        self.amount_class_l = empty
        self.start_end_l = empty
        self.person_name_l = empty
        self.car_number_l = empty
        self.is_matching = False
        pages = [0]
        for page in pages:
            page_img = get_pdf_page_image(self.pdf, page)
            if page_img is not None:
                self.contract_name_l = get_image_text_using_ocr(page_img.crop((193, 3507, 2182, 3607)))
                self.insurer_name_l = get_image_text_using_ocr(page_img.crop((193, 3609, 1450, 3702)))
                self.is_matching = self._is_match()
                if self.is_matching:
                    self._continue_extracting(page_img)
                    self._log_extracted_values()
                    break

    def _continue_extracting(self, page_img):
        self.insurance_number_l = get_image_digits_using_ocr(page_img.crop((1476, 996, 2544, 1122)))
        self.start_end_l = get_image_text_using_ocr(page_img.crop((193, 5115, 4788, 5223)))
        self.amount_class_l = get_image_text_using_ocr(page_img.crop((193, 5211, 4788, 5313)))
        self.person_name_l = get_image_text_using_ocr(page_img.crop((954, 3945, 2728, 4114)))
        self.car_number_l = get_ro_car_number_from_image(page_img.crop((193, 1306, 1454, 1373)))
        self.insurance_number_l = remove_slashes(self.insurance_number_l)



    def _log_extracted_values(self):
        self.logger.debug(
            "contract_name_p: %s, insurer_name_p: %s, insurance_number_p: %s, start_end_p: %s, amount_class_p: %s, person_name_p: %s, car_number_p: %s",
            self.contract_name_l, self.insurer_name_l, self.insurance_number_l, self.start_end_l, self.amount_class_l,
            self.person_name_l, self.car_number_l)

    def is_match(self):
        return self.is_matching

    def _is_match(self):
        is_rca = is_RCA(self.contract_name_l)
        return is_rca and self.get_insurer_name() == "GROUPAMA ASIGURĂRI"

    def get_insurer_short_name(self):
        return "GROUPAMA"

    def get_insurer_name(self):
        match = re.search(r'(.*)S\.A\.', self.insurer_name_l)
        if match:
            return clean_text(match.group(1))
        else:
            return None

    def get_insurance_number(self):

        match = re.search(r'([\s\d]*)', self.insurance_number_l)
        if match:
            txt = match.group(1).strip()
            txt = re.sub(r'\s', "", txt)
            return txt
        else:
            return None

    def get_insurance_class(self):
        match = re.search(r'Clasă\s*Bonus-Malus:(.*)', self.amount_class_l)
        if match:
            return clean_text(match.group(1))
        else:
            return None

    def get_start_date(self):
        return get_date(self.start_end_l, r'Contract\s*de\s*la(.*)-(.*)-(.*)până')

    def get_expiration_date(self):
        return get_date(self.start_end_l, r'până\s*la(.*)-(.*)-(.*)Contract emis')

    def get_contract_date(self):
        return get_date(self.start_end_l, r'Contract\s*emis\s*în\s*data\s*de(.*)-(.*)-(.*)')

    def get_person_name(self):
        return clean_text(self.person_name_l)

    def get_car_number(self):
        return get_car_number(self.car_number_l)

    def get_insurance_amount(self):
        match = re.search(r'Prima\s*de\s*asigurare(.*)LEI', self.amount_class_l)
        if match:
            return clean_text(match.group(1))
        else:
            return None