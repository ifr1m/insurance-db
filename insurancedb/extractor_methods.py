import datetime
import re


def clean_text(text: str):
    result = text.strip()
    result = result.replace("_", "")
    return result


def get_date(text, regex):
    match = re.search(regex, text)
    if match:
        day = int(clean_text(match.group(1)))
        month = int(clean_text(match.group(2)))
        year = int(clean_text(match.group(3)))
        result = datetime.date(year, month, day)
        return result
    else:
        return None


def diff_months(end: datetime.date, start: datetime.date):
    if end and start:
        return (end.year - start.year) * 12 + (end.month - start.month)


def get_car_number(text: str):
    match = re.search(r'\s([A-Z]{2}[0-9]{2}[A-Z]{3}|B[0-9]{2,3}[A-Z]{3})\s', text)
    if match:
        return clean_text(match.group(1))
    else:
        return None


def is_RCA(text: str):
    return re.search(r'AUTO RCA', text) is not None
