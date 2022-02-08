import abc


class BaseRcaExtractor(abc.ABC):

    def is_match(self):
        pass

    def get_insurer_short_name(self):
        pass

    def get_insurer_name(self):
        pass

    def get_insurance_number(self):
        pass

    def get_insurance_class(self):
        pass

    def get_start_date(self):
        pass

    def get_expiration_date(self):
        pass

    def get_contract_date(self):
        pass

    def get_person_name(self):
        pass

    def get_car_number(self):
        pass

    def get_insurance_amount(self):
        pass

    def get_type(self):
        return "RCA"


