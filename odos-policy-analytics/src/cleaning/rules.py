import re
from datetime import date, datetime


ERROR_TOKENS = {"#NUM!", "#VALUE!", "#REF!", "#DIV/0!", "#N/A", "#NAME?"}


def normalize_text(value):
    if value is None:
        return None
    text = re.sub(r"\s+", " ", str(value)).strip()
    if not text:
        return None
    if text.upper() in ERROR_TOKENS:
        return None
    return text


def fit_level(value):
    text = normalize_text(value)
    if text is None or text.lower() in {"n/a", "-", "nan"}:
        return None
    if "ไม่สอดคล้อง" in text:
        return 0
    if "น้อย" in text:
        return 1
    if "ปานกลาง" in text:
        return 2
    if "มาก" in text:
        return 3
    return None


def government_preference_flag(value):
    text = normalize_text(value)
    if text is None:
        return None
    if text.startswith("ต้องการ"):
        return 1
    if text.startswith("ไม่ต้องการ"):
        return 0
    return None


def parse_gpa(value):
    number = parse_float(value)
    if number is None:
        return None
    if 0 <= number <= 4:
        return round(number, 3)
    if 0 <= number <= 100:
        return round(number / 25, 3)
    return None


def parse_float(value):
    text = normalize_text(value)
    if text is None:
        return None
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    match = re.search(r"\d+(?:[\.,]\d+)?", text)
    if not match:
        return None
    return float(match.group(0).replace(",", "."))


def parse_income_monthly_estimate(value):
    text = normalize_text(value)
    if text is None:
        return None
    normalized = text.replace(",", "").replace("บาท", "").strip()
    numbers = [float(number) for number in re.findall(r"\d+(?:\.\d+)?", normalized)]
    if not numbers:
        return None
    if "ขึ้นไป" in text:
        estimate = numbers[0]
    elif len(numbers) >= 2:
        estimate = (numbers[0] + numbers[1]) / 2
    else:
        estimate = numbers[0]
    return round(estimate, 2)


def parse_iso_date(value):
    value = normalize_text(value) if isinstance(value, str) else value
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    text = str(value).strip()
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(text[:10], fmt).date().isoformat()
        except ValueError:
            continue
    return None


def years_between(start_value, end_value):
    start = parse_iso_date(start_value)
    end = parse_iso_date(end_value)
    if not start or not end:
        return None
    start_date = datetime.strptime(start, "%Y-%m-%d").date()
    end_date = datetime.strptime(end, "%Y-%m-%d").date()
    if end_date < start_date:
        return None
    return round((end_date - start_date).days / 365.25, 2)


def standardize_category(value, replacements=None):
    text = normalize_text(value)
    if text is None:
        return None
    normalized = text.replace("ฯ", "")
    normalized = re.sub(r"\s+", " ", normalized).strip()
    if replacements and normalized in replacements:
        return replacements[normalized]
    return normalized
