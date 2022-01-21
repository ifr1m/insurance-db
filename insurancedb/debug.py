import pathlib
from pathlib import Path

import click
import pdfplumber
import cv2
import pytesseract
from pytesseract import Output
import numpy as np

from insurancedb.extractor import AsiromRcaExtractor
from insurancedb.extractor_methods import get_pdf_page_image, get_pdf_page_text, contains_unparsed_characters


@click.command()
@click.option('--pdf', type=click.Path(path_type=pathlib.Path))
def debug_ocr(pdf: Path):
    with pdfplumber.open(pdf) as pdf_file:
        custom_config = r'-l ron --psm 6'
        pil_img = get_pdf_page_image(pdf_file, 2)
        img = np.array(pil_img)
        img = img[:, :, ::-1].copy()
        d = pytesseract.image_to_data(img, config=custom_config, output_type=Output.DICT)
        print(pytesseract.image_to_string(img, config=custom_config))
        n_boxes = len(d['text'])
        for i in range(n_boxes):
            # if int(d['conf'][i]) > 60:
                (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
                img = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), thickness=2)

        cv2.imshow('img', img)
        cv2.waitKey(0)

@click.command()
@click.option('--pdf', type=click.Path(path_type=pathlib.Path))
def debug_unparsed_characters(pdf: Path):
    for pth in pdf.rglob("*.pdf"):
        with pdfplumber.open(pth) as pdf_file:
            text = get_pdf_page_text(pdf_file, 0)
            broken = contains_unparsed_characters(text)
            if broken:
                print(pth)

@click.command()
@click.option('--pdf', type=click.Path(path_type=pathlib.Path))
def debug_extractor(pdf: Path):
    with pdfplumber.open(pdf) as pdf_file:
        extractor = AsiromRcaExtractor(pdf_file)
        extractor.is_match()




if __name__ == '__main__':
    debug_ocr()
