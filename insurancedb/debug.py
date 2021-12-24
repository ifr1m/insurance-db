import pathlib
from pathlib import Path

import click
import pdfplumber

from insurancedb.extractor import AsiromRcaExtractor


@click.command()
@click.option('--pdf', type=click.Path(path_type=pathlib.Path))
def debug_extractor(pdf: Path):
    with pdfplumber.open(pdf) as pdf_file:
        extractor = AsiromRcaExtractor(pdf_file)
        extractor.is_match()




if __name__ == '__main__':
    debug_extractor()
