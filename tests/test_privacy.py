import pytest

from src.governance.privacy import assert_no_forbidden_columns, forbidden_columns_present


def test_forbidden_columns_present():
    assert forbidden_columns_present(["odos_uid", "contact_phone"]) == ["contact_phone"]


def test_assert_no_forbidden_columns_raises():
    with pytest.raises(ValueError):
        assert_no_forbidden_columns(["odos_uid", "contract_no"])


def test_assert_no_forbidden_columns_passes():
    assert_no_forbidden_columns(["odos_uid", "province"])
