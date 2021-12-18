import abc
import functools
import re
from dataclasses import dataclass
from typing import Dict

import pdfplumber

from insurancedb.extractor_methods import get_date, clean_text, get_car_number, is_RCA, get_pdf_page_text, \
    contains_unparsed_characters, get_pdf_page_text_using_ocr


class BaseRcaExtractor(abc.ABC):

    def get_expiration_date(self):
        pass

    def get_start_date(self):
        pass

    def get_insurance_number(self):
        pass

    def get_person_name(self):
        pass

    def get_insurance_amount(self):
        pass

    def get_insurance_class(self):
        pass

    def get_contract_date(self):
        pass

    def get_insurer_name(self):
        pass

    def is_match(self):
        pass

    def get_car_number(self):
        pass

    def get_insurer_short_name(self):
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
        first_page = self.pdf.pages[0]
        self.text = first_page.extract_text()

    def get_expiration_date(self):
        return get_date(self.text, r'până la:(.*)\.(.*)\.(.*) Contract')

    def get_start_date(self):
        return get_date(self.text, r'Contract de la(.*)\.(.*)\.(.*)până la')

    def get_insurance_number(self):
        match = re.search(r'Seria(.*)Nr\.(.*)', self.text)
        if match:
            return match.group(2).strip()
        else:
            return None

    def get_person_name(self):
        match = re.search(r'Nume/Denumire Asigurat/(.*)Fel, Tip, Marca', self.text)
        if match:
            return match.group(1).strip()
        else:
            return None

    def get_insurance_amount(self, ):
        match = re.search(r'Prima de asigurare:(.*)Lei,', self.text)
        if match:
            return clean_text(match.group(1))
        else:
            return None

    def get_insurance_class(self):
        match = re.search(r'Clasa Bonus-Malus:(.*),  Tarif de decontare', self.text)
        if match:
            return clean_text(match.group(1))
        else:
            return None

    def get_contract_date(self):
        return get_date(self.text, r'Contract emis în data de:(.*)\.(.*)\.(.*) (.*):')

    def get_insurer_name(self):
        match = re.search(r'(EUROINS.*)R.C', self.text)
        if match:
            return clean_text(match.group(1))
        else:
            return None

    def get_insurer_short_name(self):
        return "EUROINS"

    def is_match(self):
        is_rca = is_RCA(self.text)
        return is_rca and self.get_insurer_name() == "EUROINS ROMÂNIA ASIGURARE REASIGURARE S.A."

    def get_car_number(self):
        return get_car_number(self.text)


@dataclass
@extractor_register
class CityInsuranceRcaExtractor(BaseRcaExtractor):
    pdf: pdfplumber.PDF = None

    def __post_init__(self):
        first_page = self.pdf.pages[0]
        self.text = first_page.extract_text()

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
        first_page = self.pdf.pages[0]
        self.text = first_page.extract_text()

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
        first_page = self.pdf.pages[0]
        self.text = first_page.extract_text()

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
        match = re.search(r'Nume / Denumire(.*)Fel, Tip, Marcă', self.text)
        if match:
            return match.group(1).strip()
        else:
            return None

    def get_insurance_amount(self):
        match = re.search(r'Prima de asigurare(.*)LEI', self.text)
        if match:
            return clean_text(match.group(1))
        else:
            return None

    def get_insurance_class(self):
        match = re.search(r'Clasă Bonus-Malus:(.*)', self.text)
        if match:
            return clean_text(match.group(1))
        else:
            return None

    def get_contract_date(self):
        return get_date(self.text, r'Contract emis în data de(.*)\.(.*)\.(.*)')

    def get_insurer_name(self):
        match = re.search(r'(GROUPAMA.*)Tel\.', self.text)
        if match:
            return clean_text(match.group(1))
        else:
            return None

    def get_insurer_short_name(self):
        return "GROUPAMA"

    def is_match(self):
        is_rca = is_RCA(self.text)
        return is_rca and self.get_insurer_name() == "GROUPAMA ASIGURĂRI S.A."

    def get_car_number(self):
        return get_car_number(self.text)


@dataclass
@extractor_register
class AllianzRcaExtractor(BaseRcaExtractor):
    pdf: pdfplumber.PDF = None

    def __post_init__(self):
        self.text = get_pdf_page_text_using_ocr(self.pdf, 2)

    def get_expiration_date(self):
        return get_date(self.text, r'la:(.*)\.(.*)\.(.*)Contract emis')

    def get_start_date(self):
        return get_date(self.text, r'Valabilitate Contract de la(.*)\.(.*)\.(.*)până')

    def get_insurance_number(self):
        match = re.search(r'Seria.*Nr\.(.*)', self.text)
        if match:
            return match.group(1).strip()
        else:
            return None

    def get_person_name(self):
        match = re.search(r'\(Nume, prenume, CNP\)([a-zA-ZăâîșțĂÂÎȘȚ\-\s]*)', self.text)
        if match:
            return match.group(1).strip()
        else:
            return None

    def get_insurance_amount(self):
        match = re.search(r'Prima de asigurare(.*)RON Clasa Bonus', self.text)
        if match:
            return clean_text(match.group(1))
        else:
            return None

    def get_insurance_class(self):
        match = re.search(r'Clasa Bonus Malus(.*)Tarif decontare', self.text)
        if match:
            return clean_text(match.group(1))
        else:
            return None

    def get_contract_date(self):
        return get_date(self.text, r'Contract emis în data(.*)\.(.*)\.(.*)')

    def get_insurer_name(self):
        match = re.search(r'Denumire asigurator:(.*)S\.A\.', self.text)
        if match:
            return clean_text(match.group(1))
        else:
            return None

    def get_insurer_short_name(self):
        return "ALLIANZ"

    def is_match(self):
        is_rca = is_RCA(self.text)
        return is_rca and self.get_insurer_name() == "ALLIANZ - ŢIRIAC ASIGURĂRI"

    def get_car_number(self):
        return get_car_number(self.text)
