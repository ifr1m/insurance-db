import logging
from pathlib import Path
from typing import List

import pdfplumber

from insurancedb.extractors.registry import extractors_registry_map
from insurancedb.extractors.extractor_methods import diff_months

logger = logging.getLogger(__name__)


def process_paths(paths: List[Path]):
    logger.info("Processing %d files.", len(paths))
    data = []
    for pdf_path in paths:
        with pdfplumber.open(pdf_path) as pdf:
            processed = False
            for extractor_key, extractor_cls in extractors_registry_map.items():
                extractor = extractor_cls(pdf)
                if extractor.is_match():
                    processed = True
                    logger.info("%s :-> %s", extractor_cls.__name__, {str(pdf_path)})
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
                pdf_data = [f"Unprocessed {str(pdf_path)}", None, None, None, None, None, None, None, None, None, None,
                            pdf_path.name]
                data.append(pdf_data)

    return data
