import datetime
import re

import pdfplumber


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


def get_pdf_page_text(pdf: pdfplumber.PDF, page: int):
    text = ""
    if len(pdf.pages) >= page + 1:
        pdf_page = pdf.pages[page]
        text = pdf_page.extract_text()
    return text


def contains_unparsed_characters(text: str):
    return re.search('\(cid:[0-9]{2,3}\)', text) is not None


def is_RCA(text: str):
    return re.search(r'AUTO\s*RCA', text) is not None
