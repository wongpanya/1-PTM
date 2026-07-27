import re


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
