FORBIDDEN_COLUMNS = {
    "contact_name",
    "contact_phone",
    "contract_no",
    "employment_cert_doc_no",
    "workplace_address",
    "officer_notes",
    "other_comments",
    "employer",
    "job_title",
    "income_raw",
    "gpa_raw",
}


def forbidden_columns_present(columns) -> list[str]:
    return sorted(FORBIDDEN_COLUMNS.intersection(set(columns)))


def assert_no_forbidden_columns(columns) -> None:
    present = forbidden_columns_present(columns)
    if present:
        raise ValueError(f"Forbidden columns present: {', '.join(present)}")
