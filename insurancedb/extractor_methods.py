import datetime
import re

import PIL
import cv2
import numpy as np
import pandas as pd
import pdfplumber
import pytesseract
from PIL import Image

from insurancedb.utils import get_project_root

resources_dir = get_project_root() / "resources"

START_X = 0
START_Y = 1
END_X = 2
END_Y = 3
SCORE = 4
METHODS = 5


def clean_text(text: str):
    result = text.strip()
    result = result.replace("_", "")
    return result


def get_date(text, regex):
    match = re.search(regex, text)
    if match:
        day = int(clean_text(match.group(1)))
        month = int(clean_text(match.group(2)))
        year = int(clean_text(match.group(3)))
        result = datetime.date(year, month, day)
        return result
    else:
        return None


def diff_months(end: datetime.date, start: datetime.date):
    if end and start:
        return (end.year - start.year) * 12 + (end.month - start.month)


def get_car_number(text: str):
    match = re.search(r'([A-Z]{2}[0-9]{2}[A-Z]{3}|B[0-9]{2,3}[A-Z]{3})', text)
    if match:
        return clean_text(match.group(1))
    else:
        return None


def get_ro_car_number_from_image(car_number_image_l):
    ro_car_number_tess_patterns_path = resources_dir / "ro-car-number-tess.patterns"
    car_number_image_l = add_margin(car_number_image_l, 10, 10, 10, 10, (255, 255, 255))
    return get_image_text_using_ocr(car_number_image_l,
                                    ocr_config=r'-l eng --psm 7 --user-patterns ' + str(ro_car_number_tess_patterns_path))


def get_pdf_page_text(pdf: pdfplumber.PDF, page: int):
    text = ""
    if len(pdf.pages) >= page + 1:
        pdf_page = pdf.pages[page]
        text = pdf_page.extract_text()
    return text


def get_pdf_page_text_using_ocr(pdf: pdfplumber.PDF, page: int, ocr_config=r'-l ron --psm 6'):
    img = get_pdf_page_image(pdf, page)
    return pytesseract.image_to_string(img, config=ocr_config)


def get_pdf_page_text_using_ocr(pdf: pdfplumber.PDF, pages: [], ocr_config=r'-l ron --psm 6'):
    txt = ""
    for page in pages:
        # txt = txt + get_pdf_page_text(pdf, page)
        img = get_pdf_page_image(pdf, page)
        txt = txt + get_image_text_using_ocr(img, ocr_config)
    return txt


def get_image_text_using_ocr(image, ocr_config=r'-l ron --psm 7'):
    return pytesseract.image_to_string(image, config=ocr_config)


def get_image_digits_using_ocr(image, ocr_config=r'-l eng --psm 7 -c tessedit_char_whitelist=0123456789'):
    return pytesseract.image_to_string(image, config=ocr_config)


def get_pdf_page_image(pdf: pdfplumber.PDF, page: int, resolution=600):
    img = None
    if len(pdf.pages) >= page + 1:
        pdf_page = pdf.pages[page]
        img = pdf_page.to_image(resolution=resolution).original.convert('RGB')
    return img


def contains_unparsed_characters(text: str):
    return re.search('\(cid:[0-9]{2,3}\)', text) is not None


def is_RCA(text: str):
    return re.search(r'AUTO\s*RCA', text) is not None


def remove_slashes(txt):
    return re.sub(r'/', "", txt)


def add_margin(pil_img, top, right, bottom, left, color):
    """
    source https://github.com/nkmk/python-snippets/blob/0f6b4672097e91b00e51775ae1932aaf47b8977a/notebook/my_lib/imagelib.py#L4-L10

    """
    width, height = pil_img.size
    new_width = width + right + left
    new_height = height + top + bottom
    result = Image.new(pil_img.mode, (new_width, new_height), color)
    result.paste(pil_img, (left, top))
    return result


def find_position_of_template(input_img: np.ndarray, template: np.ndarray, threshold=0.8, input_mask=None,
                              use_inverted_template_as_mask=True):
    """

    source https://docs.opencv.org/4.5.2/d4/dc6/tutorial_py_template_matching.html

    """
    gray_img = cv2.cvtColor(input_img, cv2.COLOR_BGR2GRAY)
    gray_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    mask = None
    if input_mask is not None:
        mask = input_mask
    if use_inverted_template_as_mask and input_mask is None:
        mask = cv2.bitwise_not(gray_template)

    w, h = gray_template.shape[::-1]
    # Try all 6 methods
    methods = ['cv2.TM_CCOEFF_NORMED', 'cv2.TM_CCORR_NORMED', 'cv2.TM_SQDIFF_NORMED']

    def detect_positions():
        for meth in methods:
            img = gray_img.copy()
            method = eval(meth)
            # Apply template Matching
            res = cv2.matchTemplate(img, gray_template, method, mask=mask)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
            if method in [cv2.TM_SQDIFF_NORMED]:
                top_left = min_loc
                score = 1 - min_val
            else:
                top_left = max_loc
                score = max_val
            bottom_right = (top_left[0] + w, top_left[1] + h)
            yield int(top_left[0]), int(top_left[1]), int(bottom_right[0]), int(bottom_right[1]), score, meth

    result = pd.DataFrame(data=list(detect_positions()),
                          columns=["START_X", "START_Y", "END_X", "END_Y", "SCORE", "METHOD"])
    # remove rows that contain inf -inf nan
    result = result[~result.isin([np.nan, np.inf, -np.inf]).any(1)]
    result = result[result["SCORE"] > threshold].sort_values("SCORE", ascending=False)
    return result.head(1)


def get_top_left_position_of_template(input_img: np.ndarray, template: np.ndarray):
    bbox_df = find_position_of_template(input_img, template).head(1)
    return bbox_df[START_X], bbox_df[START_Y]


def to_opencv(pil_image: PIL.Image) -> np.ndarray:
    open_cv_image = np.array(pil_image)
    cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2RGB)
    return open_cv_image


def show_image_with_bboxes(img: np.ndarray, bboxes: pd.DataFrame):
    c_img = img.copy()
    bboxes.apply(lambda x: to_bboxes_rectangles(x, c_img), axis=1)
    Image.fromarray(c_img).show()


def to_bboxes_rectangles(bbox, img: np.ndarray):
    top_left = (bbox[START_X], bbox[START_Y])
    bottom_right = (bbox[END_X], bbox[END_Y])
    bottom_left = (bbox[START_X], bbox[END_Y])
    cv2.rectangle(img, top_left, bottom_right, (0, 255, 0), thickness=10)
    font = cv2.FONT_HERSHEY_SIMPLEX
    txt = str(bbox[METHODS]) + " : " + str(bbox[SCORE])
    cv2.putText(img, txt, bottom_left, font, 4, (0, 0, 255), 2, cv2.LINE_AA)
