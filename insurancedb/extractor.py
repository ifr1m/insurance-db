import abc
import functools
import re
from typing import Dict

from insurancedb.extractor_methods import get_date, clean_text, diff_months, get_car_number


class BaseRcaExtractor(abc.ABC):

    def get_expiration_date(self, text: str):
        pass

    def get_start_date(self, text):
        pass

    def get_insurance_number(self, text: str):
        pass

    def get_person_name(self, text: str):
        pass

    def get_insurance_amount(self, text: str):
        pass

    def get_insurance_class(self, text: str):
        pass

    def get_contract_date(self, text):
        pass

    def get_insurer_name(self, text: str):
        pass

    def is_match(self, text: str):
        pass

    def get_car_number(self, text: str):
        pass

    def get_insurer_short_name(self):
        pass

    def get_type(self):
        return "RCA"


registry_map: Dict[str, BaseRcaExtractor] = {}


def register(cls):
    registry_map[cls.__name__.lower()] = cls()
    return cls


extractor_register = functools.partial(register)


@extractor_register
class EuroInsRcaExtractor(BaseRcaExtractor):

    def get_expiration_date(self, text: str):
        return get_date(text, r'până la:(.*)\.(.*)\.(.*) Contract')

    def get_start_date(self, text):
        return get_date(text, r'Contract de la(.*)\.(.*)\.(.*)până la')

    def get_insurance_number(self, text: str):
        match = re.search(r'Seria(.*)Nr\.(.*)', text)
        if match:
            return match.group(2).strip()
        else:
            return None

    def get_person_name(self, text: str):
        match = re.search(r'Nume/Denumire Asigurat/(.*)Fel, Tip, Marca', text)
        if match:
            return match.group(1).strip()
        else:
            return None

    def get_insurance_amount(self, text: str):
        match = re.search(r'Prima de asigurare:(.*)Lei,', text)
        if match:
            return clean_text(match.group(1))
        else:
            return None

    def get_insurance_class(self, text: str):
        match = re.search(r'Clasa Bonus-Malus:(.*),  Tarif de decontare', text)
        if match:
            return clean_text(match.group(1))
        else:
            return None

    def get_contract_date(self, text: str):
        return get_date(text, r'Contract emis în data de:(.*)\.(.*)\.(.*) (.*):')

    def get_insurer_name(self, text: str):
        match = re.search(r'(EUROINS.*)R.C', text)
        if match:
            return clean_text(match.group(1))
        else:
            return None

    def get_insurer_short_name(self):
        return "EUROINS"

    def is_match(self, text: str):
        return self.get_insurer_name(text) == "EUROINS ROMÂNIA ASIGURARE REASIGURARE S.A."

    def get_car_number(self, text: str):
        return get_car_number(text)


@extractor_register
class CityInsuranceRcaExtractor(BaseRcaExtractor):

    def get_expiration_date(self, text: str):
        return get_date(text, r'pana la(.*)/(.*)/(.*)Contract')

    def get_start_date(self, text):
        return get_date(text, r'Valabilitate Contract de la(.*)/(.*)/(.*)pana la')

    def get_insurance_number(self, text: str):
        match = re.search(r'Seria(.*)Nr\.(.*)', text)
        if match:
            return match.group(2).strip()
        else:
            return None

    def get_person_name(self, text: str):
        match = re.search(r'Nume/Denumire Asigurat Fel, Tip, Marca.*[\r\n]+([^\r\n]+)', text)
        if match:
            return match.group(1).strip()
        else:
            return None

    def get_insurance_amount(self, text: str):
        match = re.search(r'Prima totala(.*)Lei', text)
        if match:
            return clean_text(match.group(1))
        else:
            return None

    def get_insurance_class(self, text: str):
        match = re.search(r'Clasa Bonus-Malus(.*)', text)
        if match:
            return clean_text(match.group(1))
        else:
            return None

    def get_contract_date(self, text: str):
        return get_date(text, r'Contract emis in data de(.*)/(.*)/(.*), ora')

    def get_insurer_name(self, text: str):
        match = re.search(r'DENUMIRE ASIGURATOR:(.*)R.C', text)
        if match:
            return clean_text(match.group(1))
        else:
            return None

    def get_insurer_short_name(self):
        return "CITY"

    def get_insurance_interval(self, text: str):
        exp = self.get_expiration_date(text)
        start = self.get_start_date(text)
        return diff_months(exp, start)

    def is_match(self, text: str):
        return self.get_insurer_name(text) == "CITY INSURANCE S.A."

    def get_car_number(self, text: str):
        return get_car_number(text)
