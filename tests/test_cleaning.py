from src.cleaning.rules import fit_level, government_preference_flag, normalize_text


def test_normalize_text_handles_errors_and_spaces():
    assert normalize_text("  A\n B  ") == "A B"
    assert normalize_text("#NUM!") is None
    assert normalize_text("") is None


def test_fit_level_mapping():
    assert fit_level("ไม่สอดคล้อง") == 0
    assert fit_level("สอดคล้องน้อย") == 1
    assert fit_level("สอดคล้องปานกลาง") == 2
    assert fit_level("สอดคล้องมาก") == 3
    assert fit_level("N/A") is None


def test_government_preference_flag():
    assert government_preference_flag("ต้องการ") == 1
    assert government_preference_flag("ไม่ต้องการ") == 0
    assert government_preference_flag("N/A") is None
