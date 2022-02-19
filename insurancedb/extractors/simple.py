import re
from dataclasses import dataclass

import pdfplumber

from insurancedb.extractors.base import BaseRcaExtractor
from insurancedb.extractors.extractor_methods import get_pdf_page_text, is_RCA, clean_text, get_date, get_car_number
from insurancedb.extractors.registry import extractor_register


@extractor_register
@dataclass
class EuroInsRcaExtractor(BaseRcaExtractor):
    file_name: str
    pdf: pdfplumber.PDF = None

    def __post_init__(self):
        self.text = ""
        if self._is_file_name_matching():
            self.text = get_pdf_page_text(self.pdf, 0)

    def _is_file_name_matching(self):
        return re.search(self.get_insurer_short_name(), self.file_name, re.IGNORECASE) is not None or \
               re.search("RO16H16DV", self.file_name, re.IGNORECASE) is not None

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
    file_name: str
    pdf: pdfplumber.PDF = None

    def __post_init__(self):
        self.text = ""
        if self._is_file_name_matching():
            self.text = get_pdf_page_text(self.pdf, 0)

    def _is_file_name_matching(self):
        return re.search(self.get_insurer_short_name(), self.file_name, re.IGNORECASE) is not None or \
               re.search("RO25C25HP", self.file_name, re.IGNORECASE) is not None

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
    file_name: str
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


@extractor_register
@dataclass
class AsiromRcaExtractor(BaseRcaExtractor):
    file_name: str
    pdf: pdfplumber.PDF = None

    def __post_init__(self):
        self.text = ""
        if self._is_file_name_matching():
            self.text = get_pdf_page_text(self.pdf, 0)

    def _is_file_name_matching(self):
        return re.search(self.get_insurer_short_name(), self.file_name, re.IGNORECASE) is not None or \
               re.search("XZ", self.file_name, re.IGNORECASE) is not None

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
    file_name: str
    pdf: pdfplumber.PDF = None

    def __post_init__(self):
        self.text = ""
        if self._is_file_name_matching():
            self.text = get_pdf_page_text(self.pdf, 4)

    def _is_file_name_matching(self):
        return re.search(self.get_insurer_short_name(), self.file_name, re.IGNORECASE) is not None or \
               re.search("RO05M3NP", self.file_name, re.IGNORECASE) is not None

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
    file_name: str
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
