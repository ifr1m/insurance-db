import pathlib
from pathlib import Path

import click
import pdfplumber
import cv2
import pytesseract
from pytesseract import Output
import numpy as np

from insurancedb.extractor_methods import get_pdf_page_image


@click.command()
@click.option('--pdf', type=click.Path(path_type=pathlib.Path))
def debug(pdf: Path):
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


if __name__ == '__main__':
    debug()
