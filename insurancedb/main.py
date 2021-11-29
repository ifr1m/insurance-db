import logging
import pathlib
import sys
from pathlib import Path

import click
import pandas as pd
import pdfplumber

from insurancedb.extractor import registry_map
from insurancedb.extractor_methods import diff_months

def config_console_log():
    log_formatter = logging.Formatter(
        "%(asctime)s [%(threadName)-12.12s] [%(name)-20.20s] [%(levelname)-5.5s]  %(message)s")
    root_logger = logging.getLogger()
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_formatter)
    root_logger.addHandler(console_handler)
    root_logger.setLevel(logging.INFO)
    logging.getLogger("pdfminer").setLevel(logging.WARNING)

@click.command()
@click.option('--pdfs_dir', type=click.Path(path_type=pathlib.Path))
@click.option('--out_dir', type=click.Path(path_type=pathlib.Path), required=False)
def create_db(pdfs_dir: Path, out_dir: Path):
    config_console_log()
    logger = logging.getLogger(__name__)
    if out_dir is None:
        out_dir = pdfs_dir

    data = []
    for pdf_path in sorted(pdfs_dir.glob("*.pdf")):
        with pdfplumber.open(pdf_path) as pdf:
            logger.info("Processing file: %s", str(pdf_path))
            first_page = pdf.pages[0]
            text = first_page.extract_text()

            for extractor_key, extractor in registry_map.items():
                if extractor.is_match(text):
                    # NR.CRT
                    # ASIGURATOR
                    # NUMAR POLITA
                    # CLASA B/M
                    # DATA EMITERE
                    # DATA EXPIRARE
                    # NUME CLIENT
                    # NUMAR DE TELEFON
                    # TIP ASIGURARE
                    # NUMAR INMATRICULARE
                    # PERIODA DE ASIGURARE
                    # VALOARE POLITA - prima de asigurare
                    # PDF
                    start_date = extractor.get_start_date(text)
                    expiration_date = extractor.get_expiration_date(text)
                    interval = diff_months(expiration_date, start_date)

                    pdf_data = [extractor.get_insurer_short_name(), extractor.get_insurance_number(text),
                                extractor.get_insurance_class(text),
                                extractor.get_contract_date(text), expiration_date,
                                extractor.get_person_name(text), None, extractor.get_type(),
                                extractor.get_car_number(text), interval,
                                extractor.get_insurance_amount(text), pdf_path.name]

                    data.append(pdf_data)

    df = pd.DataFrame(data, columns=['ASIGURATOR', "NUMAR POLITA", "CLASA B/M", "DATA EMITERE", "DATA EXPIRARE",
                                     "NUME CLIENT", "NUMAR DE TELEFON", "TIP ASIGURARE","NUMAR INMATRICULARE",
                                     "PERIODA DE ASIGURARE", "VALOARE POLITA", "POLITA PDF"])
    df["DATA EMITERE"] = df["DATA EMITERE"].astype("M8")
    df["DATA EXPIRARE"] = df["DATA EXPIRARE"].astype("M8")

    df["DATA EMITERE"] = df["DATA EMITERE"].dt.strftime("%d.%m.%y")
    df["DATA EXPIRARE"] = df["DATA EXPIRARE"].dt.strftime("%d.%m.%y")

    df.to_csv(str(out_dir / 'db.csv'), index_label='NR.CRT', encoding='utf-8')


if __name__ == '__main__':
    create_db()
