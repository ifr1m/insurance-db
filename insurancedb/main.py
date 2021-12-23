import pathlib
from multiprocessing import Pool, cpu_count, current_process
from pathlib import Path
from typing import List

import click
import pandas as pd
import pdfplumber

from insurancedb.extractor import registry_map
from insurancedb.extractor_methods import diff_months


# this does not work wit parallel processing
# def config_console_log():
#     log_formatter = logging.Formatter(
#         "%(asctime)s [%(threadName)-12.12s] [%(name)-20.20s] [%(levelname)-5.5s]  %(message)s")
#     root_logger = logging.getLogger()
#     console_handler = logging.StreamHandler(sys.stdout)
#     console_handler.setFormatter(log_formatter)
#     root_logger.addHandler(console_handler)
#     root_logger.setLevel(logging.INFO)
#     logging.getLogger("pdfminer").setLevel(logging.WARNING)


def chunk_even_groups(lst, n_groups):
    approx_sizes = len(lst) / n_groups
    for i in range(n_groups):
        yield lst[int(i * approx_sizes):int((i + 1) * approx_sizes)]


@click.command()
@click.option('--pdfs_dir', type=click.Path(path_type=pathlib.Path))
@click.option('--out_dir', type=click.Path(path_type=pathlib.Path), required=False)
def create_db(pdfs_dir: Path, out_dir: Path):
    if out_dir is None:
        out_dir = pdfs_dir

    paths = list(pdfs_dir.glob("*.pdf"))
    data = process_paths(paths)

    save_data(data, out_dir)


@click.command()
@click.option('--pdfs_dir', type=click.Path(path_type=pathlib.Path))
@click.option('--out_dir', type=click.Path(path_type=pathlib.Path), required=False)
def create_db_parallel(pdfs_dir: Path, out_dir: Path):
    if out_dir is None:
        out_dir = pdfs_dir

    paths = list(pdfs_dir.glob("*.pdf"))
    paths_chunked = list(chunk_even_groups(paths, cpu_count()))

    with Pool(cpu_count()) as pool:
        data_parallel = pool.map(process_paths, paths_chunked)
        data = [item for sublist in data_parallel for item in sublist]

    save_data(data, out_dir)


def save_data(data, out_dir):
    df = pd.DataFrame(data, columns=['ASIGURATOR', "NUMAR POLITA", "CLASA B/M", "DATA EMITERE", "DATA EXPIRARE",
                                     "NUME CLIENT", "NUMAR DE TELEFON", "TIP ASIGURARE", "NUMAR INMATRICULARE",
                                     "PERIODA DE ASIGURARE", "VALOARE POLITA", "POLITA PDF"])
    df["DATA EMITERE"] = df["DATA EMITERE"].astype("M8")
    df["DATA EXPIRARE"] = df["DATA EXPIRARE"].astype("M8")
    df["DATA EMITERE"] = df["DATA EMITERE"].dt.strftime("%d.%m.%y")
    df["DATA EXPIRARE"] = df["DATA EXPIRARE"].dt.strftime("%d.%m.%y")
    df = df.sort_values(by=['NUME CLIENT'], ignore_index=True)
    df.to_csv(str(out_dir / 'db.csv'), index_label='NR.CRT', encoding='utf-8')


def process_paths(paths: List[Path]):
    print(current_process())
    data = []
    for pdf_path in paths:
        with pdfplumber.open(pdf_path) as pdf:
            processed = False
            for extractor_key, extractor_cls in registry_map.items():
                extractor = extractor_cls(pdf)
                if extractor.is_match():
                    processed = True
                    print(f"{extractor_cls.__name__}:-> {str(pdf_path)}")
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
                    # VALOARE POLITA - prima de asigurare (totala)
                    # PDF
                    start_date = extractor.get_start_date()
                    expiration_date = extractor.get_expiration_date()
                    interval = diff_months(expiration_date, start_date)

                    pdf_data = [extractor.get_insurer_short_name(), extractor.get_insurance_number(),
                                extractor.get_insurance_class(),
                                extractor.get_contract_date(), expiration_date,
                                extractor.get_person_name(), None, extractor.get_type(),
                                extractor.get_car_number(), interval,
                                extractor.get_insurance_amount(), str(pdf_path)]

                    data.append(pdf_data)
                    break
            if not processed:
                print(extractor.text)
                print(f"Unprocessed: {str(pdf_path)} - data extractor not found")
                pdf_data = [f"Unprocessed {str(pdf_path)}", None, None, None, None, None, None, None, None, None, None,
                            pdf_path.name]
                data.append(pdf_data)

    return data
# 6	Unprocessed tricky-examples/polita-RO19A19PD21187837.pdf											polita-RO19A19PD21187837.pdf
# 9	Unprocessed tricky-examples/polita-XZ010424610(1).pdf											polita-XZ010424610(1).pdf
# 10Unprocessed tricky-examples/polita-RO05M3NP006540166.pdf											polita-RO05M3NP006540166.pdf
# https://nanonets.com/blog/ocr-with-tesseract/
#allianz, groupama are with cid problems

if __name__ == '__main__':
    create_db()
