import abc
import functools
import re
from dataclasses import dataclass
from typing import Dict

import cv2 as cv
import numpy as np
import pdfplumber

from insurancedb.extractor_methods import get_date, clean_text, get_car_number, is_RCA, get_pdf_page_text, \
    get_pdf_page_image, get_image_text_using_ocr, get_image_digits_using_ocr, remove_slashes, \
    get_ro_car_number_from_image, to_opencv, find_position_of_template
from insurancedb.utils import get_project_root

resources_dir = get_project_root() / "resources"


class BaseRcaExtractor(abc.ABC):

    def is_match(self):
        pass

    def get_insurer_short_name(self):
        pass

    def get_insurer_name(self):
        pass

    def get_insurance_number(self):
        pass

    def get_insurance_class(self):
        pass

    def get_start_date(self):
        pass

    def get_expiration_date(self):
        pass

    def get_contract_date(self):
        pass

    def get_person_name(self):
        pass

    def get_car_number(self):
        pass

    def get_insurance_amount(self):
        pass

    def get_type(self):
        return "RCA"


registry_map: Dict[str, BaseRcaExtractor.__class__] = {}


def register(cls):
    registry_map[cls.__name__.lower()] = cls
    return cls


extractor_register = functools.partial(register)


@extractor_register
@dataclass
class EuroInsRcaExtractor(BaseRcaExtractor):
    pdf: pdfplumber.PDF = None

    def __post_init__(self):
        self.text = get_pdf_page_text(self.pdf, 0)

    def is_match(self):
        is_rca = is_RCA(self.text)
        return is_rca and self.get_insurer_name() == "EUROINS ROMÂNIA ASIGURARE REASIGURARE S.A."

    def get_insurer_short_name(self):
        return "EUROINS"

    def get_insurer_name(self):
        match = re.search(r'(EUROINS.*)R.C', self.text)
        if match:
            return clean_text(match.group(1))
        else:
            return None

    def get_insurance_number(self):
        match = re.search(r'Seria(.*)Nr\.(.*)', self.text)
        if match:
            return match.group(2).strip()
        else:
            return None

    def get_insurance_class(self):
        match = re.search(r'Clasa Bonus-Malus:(.*),  Tarif de decontare', self.text)
        if match:
            return clean_text(match.group(1))
        else:
            return None

    def get_start_date(self):
        return get_date(self.text, r'Contract de la(.*)\.(.*)\.(.*)până la')

    def get_expiration_date(self):
        return get_date(self.text, r'până la:(.*)\.(.*)\.(.*) Contract')

    def get_contract_date(self):
        return get_date(self.text, r'Contract emis în data de:(.*)\.(.*)\.(.*) (.*):')

    def get_person_name(self):
        match = re.search(r'Nume/Denumire Asigurat/(.*)Fel, Tip, Marca', self.text)
        if match:
            return match.group(1).strip()
        else:
            return None

    def get_car_number(self):
        return get_car_number(self.text)

    def get_insurance_amount(self, ):
        match = re.search(r'Prima de asigurare:(.*)Lei,', self.text)
        if match:
            return clean_text(match.group(1))
        else:
            return None


@dataclass
@extractor_register
class CityInsuranceRcaExtractor(BaseRcaExtractor):
    pdf: pdfplumber.PDF = None

    def __post_init__(self):
        self.text = get_pdf_page_text(self.pdf, 0)

    def get_expiration_date(self):
        return get_date(self.text, r'pana la(.*)/(.*)/(.*)Contract')

    def get_start_date(self):
        return get_date(self.text, r'Valabilitate Contract de la(.*)/(.*)/(.*)pana la')

    def get_insurance_number(self):
        match = re.search(r'Seria(.*)Nr\.(.*)', self.text)
        if match:
            return match.group(2).strip()
        else:
            return None

    def get_person_name(self):
        match = re.search(r'Nume/Denumire Asigurat Fel, Tip, Marca.*[\r\n]+([^\r\n]+)', self.text)
        if match:
            return match.group(1).strip()
        else:
            return None

    def get_insurance_amount(self):
        match = re.search(r'Prima totala(.*)Lei', self.text)
        if match:
            return clean_text(match.group(1))
        else:
            return None

    def get_insurance_class(self):
        match = re.search(r'Clasa Bonus-Malus(.*)', self.text)
        if match:
            return clean_text(match.group(1))
        else:
            return None

    def get_contract_date(self):
        return get_date(self.text, r'Contract emis in data de(.*)/(.*)/(.*), ora')

    def get_insurer_name(self):
        match = re.search(r'DENUMIRE ASIGURATOR:(.*)R.C', self.text)
        if match:
            return clean_text(match.group(1))
        else:
            return None

    def get_insurer_short_name(self):
        return "CITY"

    def is_match(self):
        is_rca = is_RCA(self.text)
        return is_rca and self.get_insurer_name() == "CITY INSURANCE S.A."

    def get_car_number(self):
        return get_car_number(self.text)


@dataclass
@extractor_register
class GraweRcaExtractor(BaseRcaExtractor):
    pdf: pdfplumber.PDF = None

    def __post_init__(self):
        self.text = get_pdf_page_text(self.pdf, 0)

    def get_expiration_date(self):
        return get_date(self.text, r'până la(.*)\.(.*)\.(.*)Contract')

    def get_start_date(self):

        return get_date(self.text, r'Valabilitate Contract de la(.*)\.(.*)\.(.*)până la')

    def get_insurance_number(self):
        match = re.search(r'Seria(.*)Nr\.(.*)', self.text)
        if match:
            return match.group(2).strip()
        else:
            return None

    def get_person_name(self):
        match = re.search(r'Nume/Denumire Asigurat:(.*)Fel, Tip, Marcă', self.text)
        if match:
            return match.group(1).strip()
        else:
            return None

    def get_insurance_amount(self):
        match = re.search(r'Primă de asigurare(.*)Lei', self.text)
        if match:
            return clean_text(match.group(1))
        else:
            return None

    def get_insurance_class(self):
        match = re.search(r'Clasă Bonus-Malus(.*)', self.text)
        if match:
            return clean_text(match.group(1))
        else:
            return None

    def get_contract_date(self):
        return get_date(self.text, r'Contract emis în data de(.*)\.(.*)\.(.*)')

    def get_insurer_name(self):
        match = re.search(r'(GRAWE.*)R.C', self.text)
        if match:
            return clean_text(match.group(1))
        else:
            return None

    def get_insurer_short_name(self):
        return "GRAWE"

    def is_match(self):
        is_rca = is_RCA(self.text)
        return is_rca and self.get_insurer_name() == "GRAWE România Asigurare SA"

    def get_car_number(self):
        return get_car_number(self.text)


@dataclass
@extractor_register
class GroupamaRcaExtractor(BaseRcaExtractor):
    pdf: pdfplumber.PDF = None

    def __post_init__(self):
        empty = ""
        self.contract_name_p = empty
        self.insurer_name_p = empty
        self.insurance_number_p = empty
        self.amount_class_p = empty
        self.start_end_p = empty
        self.get_person_name_p = empty
        self.car_number_p = empty
        self.is_matching = False
        pages = [0]
        for page in pages:
            page_img = get_pdf_page_image(self.pdf, page)
            self.contract_name_p = get_image_text_using_ocr(page_img.crop((193, 3507, 2182, 3607)))
            self.insurer_name_p = get_image_text_using_ocr(page_img.crop((193, 3609, 1450, 3702)))
            self.is_matching = self._is_match()
            if self.is_matching:
                self._continue_extracting(page_img)
                break

    def _continue_extracting(self, page_img):
        self.insurance_number_p = get_image_digits_using_ocr(page_img.crop((1476, 996, 2544, 1122)))
        self.start_end_p = get_image_text_using_ocr(page_img.crop((193, 5115, 4788, 5223)))
        self.amount_class_p = get_image_text_using_ocr(page_img.crop((193, 5211, 4788, 5313)))
        self.get_person_name_p = get_image_text_using_ocr(page_img.crop((954, 3945, 2728, 4114)))
        self.car_number_p = get_ro_car_number_from_image(page_img.crop((193, 1306, 1454, 1373)))
        # TODO remove
        print(self.car_number_p)
        self.insurance_number_p = remove_slashes(self.insurance_number_p)

    def is_match(self):
        return self.is_matching

    def _is_match(self):
        is_rca = is_RCA(self.contract_name_p)
        return is_rca and self.get_insurer_name() == "GROUPAMA ASIGURĂRI"

    def get_insurer_short_name(self):
        return "GROUPAMA"

    def get_insurer_name(self):
        match = re.search(r'(.*)S\.A\.', self.insurer_name_p)
        if match:
            return clean_text(match.group(1))
        else:
            return None

    def get_insurance_number(self):

        match = re.search(r'([\s\d]*)', self.insurance_number_p)
        if match:
            txt = match.group(1).strip()
            txt = re.sub(r'\s', "", txt)
            return txt
        else:
            return None

    def get_insurance_class(self):
        match = re.search(r'Clasă\s*Bonus-Malus:(.*)', self.amount_class_p)
        if match:
            return clean_text(match.group(1))
        else:
            return None

    def get_start_date(self):
        return get_date(self.start_end_p, r'Contract\s*de\s*la(.*)-(.*)-(.*)până')

    def get_expiration_date(self):
        return get_date(self.start_end_p, r'până\s*la(.*)-(.*)-(.*)Contract emis')

    def get_contract_date(self):
        return get_date(self.start_end_p, r'Contract\s*emis\s*în\s*data\s*de(.*)-(.*)-(.*)')

    def get_person_name(self):
        return clean_text(self.get_person_name_p)

    def get_car_number(self):
        return get_car_number(self.car_number_p)

    def get_insurance_amount(self):
        match = re.search(r'Prima\s*de\s*asigurare(.*)LEI', self.amount_class_p)
        if match:
            return clean_text(match.group(1))
        else:
            return None


@dataclass
@extractor_register
class AllianzRcaExtractor(BaseRcaExtractor):
    pdf: pdfplumber.PDF = None

    def __post_init__(self):

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
            insurer_nm_bbox = find_position_of_template(to_opencv(page_img), cv.imread(
                str(resources_dir / "insurer_nm_allianz.png")))
            if not insurer_nm_bbox.empty:
                self.anchors["insurer-nm-allianz"] = (insurer_nm_bbox.iloc[0][0],insurer_nm_bbox.iloc[0][1])
                # 160,3730,2414,3848
                # self.contract_name_l = get_image_text_using_ocr(page_img.crop((156, 3630, 2872, 3740))) #
                crop_points_dict = self._get_crop_points_dict()
                self.contract_name_l = get_image_text_using_ocr(page_img.crop(crop_points_dict["contract_name_l"]))  #
                self.insurer_name_l = get_image_text_using_ocr(page_img.crop(crop_points_dict["insurer_name_l"]))
                self.is_matching = self._is_match()
                if self.is_matching:
                    self._continue_extracting(page_img, crop_points_dict)
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
        ## self.insurance_number_p = get_image_digits_using_ocr(page_img.crop((1582, 1186, 2773, 1344)))
        ## self.insurance_number_l = get_image_digits_using_ocr(page_img.crop((3890, 3620, 4946, 3744)))
        self.insurance_number_l = get_image_digits_using_ocr(page_img.crop(crop_points_dict["insurance_number_l"]))
        # self.amount_class_l = get_image_text_using_ocr(page_img.crop((154, 5310, 4946, 5434))) #
        # self.start_end_l = get_image_text_using_ocr(page_img.crop((154, 5200, 4946, 5308))) #
        # self.get_person_name_l = get_image_text_using_ocr(page_img.crop((1252, 4054, 2796, 4240))) #
        self.amount_class_l = get_image_text_using_ocr(page_img.crop(crop_points_dict["amount_class_l"]))  #
        self.start_end_l = get_image_text_using_ocr(page_img.crop(crop_points_dict["start_end_l"]))  #
        self.person_name_l = get_image_text_using_ocr(page_img.crop(crop_points_dict["person_name_l"]))  #
        self.car_number_l = get_ro_car_number_from_image(page_img.crop(crop_points_dict["car_number_l"]))
        self.insurance_number_l = remove_slashes(self.insurance_number_l)

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


@extractor_register
@dataclass
class AsiromRcaExtractor(BaseRcaExtractor):
    pdf: pdfplumber.PDF = None

    def __post_init__(self):
        self.text = get_pdf_page_text(self.pdf, 0)

    def is_match(self):
        is_rca = is_RCA(self.text)
        return is_rca and self.get_insurer_name() == "ASIROM VIENNA INSURANCE GROUP"

    def get_insurer_short_name(self):
        return "ASIROM"

    def get_insurer_name(self):
        match = re.search(r'Asigurarea Romaneasca - (.*)S\.A\.', self.text)
        if match:
            return clean_text(match.group(1))
        else:
            return None

    def get_insurance_number(self):
        match = re.search(r'([0-9A-Za-z]+)\s*B-dul Carol I nr. 31-33', self.text)
        if match:
            return match.group(1).strip()
        else:
            return None

    def get_insurance_class(self):
        match = re.search(r'Clasă  Bonus-Malus:(.*)Prima de asigurare', self.text)
        if match:
            return clean_text(match.group(1))
        else:
            return None

    def get_start_date(self):
        return get_date(self.text, r'Valabilitate Contract  de la(.*)\.(.*)\.(.*)pâna la')

    def get_expiration_date(self):
        return get_date(self.text, r'pâna la:(.*)\.(.*)\.(.*) Contract')

    def get_contract_date(self):
        return get_date(self.text, r'Contract emis în data de(.*)\.(.*)\.(.*)ora')

    def get_person_name(self):
        match = re.search(r'Nume/Denumire Asigurat:(.*)Fel, Tip, Marca', self.text)
        if match:
            return match.group(1).strip()
        else:
            return None

    def get_car_number(self):
        return get_car_number(self.text)

    def get_insurance_amount(self, ):
        match = re.search(r'Prima de asigurare:(.*)Lei', self.text)
        if match:
            return clean_text(match.group(1))
        else:
            return None


@extractor_register
@dataclass
class GeneraliRcaExtractor(BaseRcaExtractor):
    pdf: pdfplumber.PDF = None

    def __post_init__(self):
        self.text = get_pdf_page_text(self.pdf, 4)

    def is_match(self):
        is_rca = is_RCA(self.text)
        return is_rca and self.get_insurer_name() == "GENERALI ROMANIA ASIGURARE REASIGURARE"

    def get_insurer_short_name(self):
        return "GENERALI"

    def get_insurer_name(self):
        match = re.search(r'(.*)S\.A\.', self.text)
        if match:
            return clean_text(match.group(1))
        else:
            return None

    def get_insurance_number(self):
        match = re.search(r'Seria(.*)nr\.(.*)', self.text)
        if match:
            return match.group(2).strip()
        else:
            return None

    def get_insurance_class(self):
        match = re.search(r'Clasa Bonus-Malus:(.*)', self.text)
        if match:
            return clean_text(match.group(1))
        else:
            return None

    def get_start_date(self):
        return get_date(self.text, r'Valabilitate Contract de la(.*)\.(.*)\.(.*)pana la')

    def get_expiration_date(self):
        return get_date(self.text, r'pana la(.*)\.(.*)\.(.*)Contract emis')

    def get_contract_date(self):
        return get_date(self.text, r'Contract emis in data de(.*)\.(.*)\.(.*)')

    def get_person_name(self):
        match = re.search(r'Nume/Denumire(.*)Fel, Tip, Marca', self.text)
        if match:
            return match.group(1).strip()
        else:
            return None

    def get_car_number(self):
        return get_car_number(self.text)

    def get_insurance_amount(self, ):
        match = re.search(r'Prima de asigurare:(.*)Lei', self.text)
        if match:
            return clean_text(match.group(1))
        else:
            return None


@extractor_register
@dataclass
class OmniasigRcaExtractor(BaseRcaExtractor):
    pdf: pdfplumber.PDF = None

    def __post_init__(self):
        self.text = get_pdf_page_text(self.pdf, 0)

    def is_match(self):
        is_rca = is_RCA(self.text)
        return is_rca and self.get_insurer_name() == "OMNIASIG VIENNA INSURANCE GROUP"

    def get_insurer_short_name(self):
        return "OMNIASIG"

    def get_insurer_name(self):
        match = re.search(r'(.*)S\.A\. R\.C\.', self.text)
        if match:
            return clean_text(match.group(1))
        else:
            return None

    def get_insurance_number(self):
        match = re.search(r'Seria(.*)Nr\.(.*)', self.text)
        if match:
            return match.group(2).strip()
        else:
            return None

    def get_insurance_class(self):
        match = re.search(r'Clasă Bonus Malus(.*)Tarif', self.text)
        if match:
            return clean_text(match.group(1))
        else:
            return None

    def get_start_date(self):
        return get_date(self.text, r'Valabilitate Contract de la(.*)-(.*)-(.*)până la')

    def get_expiration_date(self):
        return get_date(self.text, r'până la(.*)-(.*)-(.*)Contract emis')

    def get_contract_date(self):
        return get_date(self.text, r'Contract emis în data de(.*)-(.*)-(.*)')

    def get_person_name(self):
        match = re.search(r'Nume/Denumire Asigurat:(.*)Fel, Tip, Marcă,', self.text)
        if match:
            return match.group(1).strip()
        else:
            return None

    def get_car_number(self):
        return get_car_number(self.text)

    def get_insurance_amount(self, ):
        match = re.search(r'Primă de asigurare(.*)Lei\s*Clasă', self.text)
        if match:
            return clean_text(match.group(1))
        else:
            return None
