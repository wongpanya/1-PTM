from __future__ import annotations

import csv
from pathlib import Path
import random


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_DIR = PROJECT_ROOT / "data" / "sample"
REFERENCE_DIR = PROJECT_ROOT / "data" / "reference"

MAIN_COLUMNS = [
    "odos_uid",
    "source_id",
    "cohort",
    "round",
    "scholarship_type",
    "cohort_round",
    "sex",
    "birth_year_be",
    "high_school_track",
    "region",
    "province_code",
    "province",
    "district",
    "economic_corridor",
    "initial_status",
    "initial_country",
    "initial_field_group",
    "initial_field",
    "study_start_date",
    "study_end_dropout_date",
    "graduation_expected_date",
    "restart_thailand_date",
    "project_condition_status",
    "overall_status",
    "after_m6_status",
    "current_status",
    "current_continent",
    "current_country",
    "current_field_group",
    "current_field",
    "program_funding_years",
    "funding_period_academic_year",
    "contract_status",
    "latest_degree",
    "gpa_numeric",
    "study_duration_years",
    "ocs_report_date",
    "moe_report_date",
    "masters_country",
    "masters_field_group",
    "masters_field",
    "doctoral_country",
    "doctoral_field_group",
    "doctoral_field",
    "employment_type",
    "employment_detail",
    "employment_evidence_status",
    "workplace_province_country",
    "work_start_date",
    "income_monthly_est",
    "welfare",
    "domicile_employment_relation",
    "field_job_fit",
    "field_job_fit_level",
    "local_fit",
    "local_fit_level",
    "job_satisfaction",
    "job_satisfaction_level",
    "wants_government",
    "wants_government_flag",
    "desired_government_position",
    "wants_moe",
    "desired_agency_other",
    "target_graduation_success",
    "target_scholarship_risk",
    "target_tracking_risk",
    "target_employment_ready",
    "target_field_mismatch",
    "target_local_mismatch",
    "target_dropout",
    "target_termination",
    "split",
]

PREDICTION_COLUMNS = [
    "case_reference",
    "purpose_code",
    "cohort",
    "sex",
    "region",
    "province",
    "current_country",
    "current_field_group",
    "gpa_numeric",
    "study_duration_years",
]

PROVINCES = [
    (10, "กรุงเทพมหานคร", "กลาง", "กรุงเทพมหานคร", ""),
    (31, "บุรีรัมย์", "ตะวันออกเฉียงเหนือ", "เมืองบุรีรัมย์", ""),
    (40, "ขอนแก่น", "ตะวันออกเฉียงเหนือ", "เมืองขอนแก่น", ""),
    (50, "เชียงใหม่", "เหนือ", "เมืองเชียงใหม่", "NSEC"),
    (57, "เชียงราย", "เหนือ", "แม่สาย", "NSEC"),
    (65, "พิษณุโลก", "กลาง", "เมืองพิษณุโลก", ""),
    (73, "นครปฐม", "กลาง", "บางเลน", "CWEC"),
    (80, "นครศรีธรรมราช", "ใต้", "เมืองนครศรีธรรมราช", "SEC"),
    (21, "ระยอง", "ตะวันออก", "เมืองระยอง", "EEC"),
    (83, "ภูเก็ต", "ใต้", "เมืองภูเก็ต", "SEC"),
]

COUNTRIES = [
    ("ประเทศไทย", "เอเชีย"),
    ("ญี่ปุ่น", "เอเชีย"),
    ("สาธารณรัฐประชาชนจีน", "เอเชีย"),
    ("สาธารณรัฐเกาหลี", "เอเชีย"),
    ("สหราชอาณาจักร", "ยุโรป"),
    ("สหรัฐอเมริกา", "อเมริกาเหนือ"),
    ("สาธารณรัฐฝรั่งเศส", "ยุโรป"),
    ("ออสเตรเลีย", "โอเชียเนีย"),
]

FIELDS = [
    ("กลุ่มวิศวกรรม", "วิศวกรรมข้อมูลและระบบอัจฉริยะ", "วิศวกรรม"),
    ("กลุ่มวิทยาศาสตร์", "วิทยาศาสตร์ข้อมูล", "วิทยาศาสตร์"),
    ("กลุ่มสาธารณสุข", "สาธารณสุขศาสตร์", "สาธารณสุข"),
    ("กลุ่มบริหารจัดการ", "เศรษฐศาสตร์และนโยบายสาธารณะ", "เศรษฐศาสตร์"),
    ("กลุ่มครุศาสตร์", "ครุศาสตร์วิทยาศาสตร์", "ครูวิทยาศาสตร์"),
    ("กลุ่มเกษตรและอาหาร", "เทคโนโลยีอาหาร", "อุตสาหกรรมอาหาร"),
    ("กลุ่มดิจิทัล", "ปัญญาประดิษฐ์ประยุกต์", "AI และดิจิทัล"),
    ("กลุ่มสิ่งแวดล้อม", "พลังงานและสิ่งแวดล้อม", "สิ่งแวดล้อม"),
]

EMPLOYMENT_TYPES = [
    ("ภาครัฐ", "เจ้าหน้าที่รัฐ/อาจารย์/บุคลากรวิชาชีพ", "ภาครัฐ"),
    ("ภาคเอกชน", "พนักงานเอกชนในประเทศไทย", "ภาคเอกชน"),
    ("ผู้ประกอบการ", "ประกอบธุรกิจหรือ startup", "ผู้ประกอบการ"),
    ("ศึกษาต่อ", "ศึกษาต่อระดับสูง", "การศึกษา"),
    ("ยังไม่พบข้อมูล", "ยังไม่มีข้อมูลติดตามหลังสำเร็จ", "ไม่ระบุ"),
]


def write_csv(path: Path, rows: list[dict[str, object]], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def binary(value: bool) -> int:
    return 1 if value else 0


def build_main_rows(total_rows: int = 240) -> list[dict[str, object]]:
    rng = random.Random(20260729)
    rows: list[dict[str, object]] = []
    for idx in range(1, total_rows + 1):
        cohort = 1 + (idx - 1) % 4
        province_code, province, region, district, corridor = PROVINCES[(idx - 1) % len(PROVINCES)]
        country, continent = COUNTRIES[(idx * 3) % len(COUNTRIES)]
        init_country, _ = COUNTRIES[(idx * 5) % len(COUNTRIES)]
        field_group, field, field_short = FIELDS[(idx * 7) % len(FIELDS)]
        initial_field_group, initial_field, _ = FIELDS[(idx * 2) % len(FIELDS)]
        employment_type, employment_detail, employer_sector = EMPLOYMENT_TYPES[(idx * 11) % len(EMPLOYMENT_TYPES)]

        status_roll = idx % 12
        graduated = status_roll not in {0, 5, 9}
        dropout = status_roll == 5
        terminated = status_roll == 9
        studying = status_roll == 0
        tracking_risk = employment_type == "ยังไม่พบข้อมูล" or studying
        field_mismatch = field_group in {"กลุ่มบริหารจัดการ", "กลุ่มสิ่งแวดล้อม"} and employment_type == "ภาคเอกชน"
        local_mismatch = province not in {"กรุงเทพมหานคร", "ขอนแก่น", "เชียงใหม่"} and idx % 3 == 0
        scholarship_risk = dropout or terminated or tracking_risk or (field_mismatch and local_mismatch)
        employment_ready = graduated and employment_type not in {"ยังไม่พบข้อมูล", "ศึกษาต่อ"}

        start_year = 2004 + cohort
        expected_year = start_year + 4 + (idx % 3)
        gpa = "" if idx % 17 == 0 else round(2.15 + rng.random() * 1.75, 2)
        duration = "" if studying else round((expected_year - start_year) + (idx % 5) * 0.25, 2)
        income = "" if not employment_ready else int(18000 + (idx % 8) * 4500 + rng.randint(0, 3500))
        field_fit_level = 1 if field_mismatch else 3 if idx % 4 else 2
        local_fit_level = 1 if local_mismatch else 3 if idx % 5 else 2
        satisfaction_level = "" if not employment_ready else 1 + idx % 3
        wants_government_flag = binary(employment_type == "ภาครัฐ" or idx % 6 == 0)

        if graduated:
            project_condition_status = "สำเร็จการศึกษา"
            overall_status = "สำเร็จการศึกษาแล้ว"
            after_m6_status = "มีข้อมูลติดตามหลังสำเร็จ"
            current_status = "สำเร็จการศึกษาปริญญาตรี"
            latest_degree = "ปริญญาตรี"
        elif dropout:
            project_condition_status = "ออกจากโครงการ"
            overall_status = "ไม่สำเร็จการศึกษา"
            after_m6_status = "ไม่มีข้อมูลติดตามหลังสำเร็จ"
            current_status = "ยุติการศึกษา"
            latest_degree = ""
        elif terminated:
            project_condition_status = "ยุติสัญญา"
            overall_status = "ยุติสถานะทุน"
            after_m6_status = "ไม่มีข้อมูลติดตามหลังสำเร็จ"
            current_status = "ยุติสัญญา"
            latest_degree = ""
        else:
            project_condition_status = "กำลังศึกษา"
            overall_status = "กำลังศึกษา"
            after_m6_status = "ยังไม่ถึงรอบติดตาม"
            current_status = "กำลังศึกษา"
            latest_degree = ""

        rows.append(
            {
                "odos_uid": f"TEST{idx:05d}",
                "source_id": idx,
                "cohort": cohort,
                "round": f"รุ่น {cohort}",
                "scholarship_type": "ทุน ODOS Prototype",
                "cohort_round": f"{cohort} / รุ่น {cohort}",
                "sex": "หญิง" if idx % 2 else "ชาย",
                "birth_year_be": 2527 + cohort + (idx % 3),
                "high_school_track": "สามัญ" if idx % 4 else "อาชีวศึกษา",
                "region": region,
                "province_code": province_code,
                "province": province,
                "district": district,
                "economic_corridor": corridor,
                "initial_status": "เริ่มรับทุนและเข้าศึกษา",
                "initial_country": init_country,
                "initial_field_group": initial_field_group,
                "initial_field": initial_field,
                "study_start_date": f"{start_year}-08-01",
                "study_end_dropout_date": f"{expected_year - 1}-05-01" if dropout or terminated else "",
                "graduation_expected_date": f"{expected_year}-07-31",
                "restart_thailand_date": f"{expected_year}-10-01" if country == "ประเทศไทย" and graduated else "",
                "project_condition_status": project_condition_status,
                "overall_status": overall_status,
                "after_m6_status": after_m6_status,
                "current_status": current_status,
                "current_continent": continent,
                "current_country": country,
                "current_field_group": field_group,
                "current_field": field,
                "program_funding_years": 4,
                "funding_period_academic_year": f"{start_year}-{expected_year}",
                "contract_status": "ทำสัญญา ก.พ." if country != "ประเทศไทย" else "ทำสัญญา สกอ.",
                "latest_degree": latest_degree,
                "gpa_numeric": gpa,
                "study_duration_years": duration,
                "ocs_report_date": f"{expected_year + 1}-02-15" if graduated and country != "ประเทศไทย" else "",
                "moe_report_date": f"{expected_year + 1}-03-15" if graduated and country == "ประเทศไทย" else "",
                "masters_country": country if idx % 19 == 0 else "",
                "masters_field_group": field_group if idx % 19 == 0 else "",
                "masters_field": field_short if idx % 19 == 0 else "",
                "doctoral_country": country if idx % 41 == 0 else "",
                "doctoral_field_group": field_group if idx % 41 == 0 else "",
                "doctoral_field": field_short if idx % 41 == 0 else "",
                "employment_type": employment_type,
                "employment_detail": employment_detail,
                "employment_evidence_status": "มีหลักฐานระดับ aggregate" if employment_ready else "รอติดตาม",
                "workplace_province_country": province if employment_type == "ภาครัฐ" else "กรุงเทพมหานคร" if employment_ready else "",
                "work_start_date": f"{expected_year + 1}-01-15" if employment_ready else "",
                "income_monthly_est": income,
                "welfare": "มีสวัสดิการ" if employment_ready and idx % 2 == 0 else "",
                "domicile_employment_relation": "จังหวัดภูมิลำเนา" if not local_mismatch else "จังหวัดต่างภูมิภาค",
                "field_job_fit": "สอดคล้องน้อย" if field_mismatch else "สอดคล้องมาก" if field_fit_level == 3 else "สอดคล้องปานกลาง",
                "field_job_fit_level": field_fit_level,
                "local_fit": "สอดคล้องน้อย" if local_mismatch else "สอดคล้องมาก" if local_fit_level == 3 else "สอดคล้องปานกลาง",
                "local_fit_level": local_fit_level,
                "job_satisfaction": "" if satisfaction_level == "" else ["น้อย", "ปานกลาง", "มาก"][int(satisfaction_level) - 1],
                "job_satisfaction_level": satisfaction_level,
                "wants_government": "ต้องการ" if wants_government_flag else "ไม่ระบุ",
                "wants_government_flag": wants_government_flag,
                "desired_government_position": "งานนโยบาย/วิเคราะห์ข้อมูล" if wants_government_flag else "",
                "wants_moe": "สนใจ" if wants_government_flag and idx % 2 == 0 else "",
                "desired_agency_other": "หน่วยงานรัฐระดับจังหวัด" if wants_government_flag and idx % 3 == 0 else "",
                "target_graduation_success": binary(graduated),
                "target_scholarship_risk": binary(scholarship_risk),
                "target_tracking_risk": binary(tracking_risk),
                "target_employment_ready": binary(employment_ready),
                "target_field_mismatch": binary(field_mismatch),
                "target_local_mismatch": binary(local_mismatch),
                "target_dropout": binary(dropout),
                "target_termination": binary(terminated),
                "split": "validation" if idx % 5 == 0 else "development",
            }
        )
    return rows


def build_prediction_rows() -> list[dict[str, object]]:
    return [
        {
            "case_reference": f"CASE_{idx:03d}",
            "purpose_code": "early_support" if idx % 2 else "prototype_evaluation",
            "cohort": 1 + (idx % 4),
            "sex": "หญิง" if idx % 2 else "ชาย",
            "region": PROVINCES[idx % len(PROVINCES)][2],
            "province": PROVINCES[idx % len(PROVINCES)][1],
            "current_country": COUNTRIES[idx % len(COUNTRIES)][0],
            "current_field_group": FIELDS[idx % len(FIELDS)][0],
            "gpa_numeric": round(2.3 + (idx % 7) * 0.22, 2),
            "study_duration_years": round(3.5 + (idx % 6) * 0.5, 1),
        }
        for idx in range(1, 25)
    ]


def build_external_indicator_rows() -> list[dict[str, object]]:
    rows = []
    for year in [2024, 2025, 2026]:
        for index, (field_group, _, field_code) in enumerate(FIELDS, start=1):
            rows.append(
                {
                    "indicator_year": year,
                    "indicator_type": "workforce_demand",
                    "indicator_name": f"ความต้องการแรงงาน {field_group}",
                    "geography_level": "national",
                    "geography_code": "TH",
                    "field_code": field_code,
                    "value": 55 + index * 3 + (year - 2024) * 2,
                    "unit": "index",
                    "source": "synthetic_test_data",
                    "source_date": f"{year}-01-15",
                    "update_date": "2026-07-29",
                    "reliability_level": "test_only",
                    "note": "ข้อมูลจำลองสำหรับทดสอบระบบเท่านั้น",
                }
            )
    return rows


def main() -> None:
    rows = build_main_rows()
    development_rows = [row for row in rows if row["split"] == "development"]
    validation_rows = [row for row in rows if row["split"] == "validation"]

    write_csv(SAMPLE_DIR / "system_test_dataset_no_pii.csv", rows, MAIN_COLUMNS)
    write_csv(SAMPLE_DIR / "system_test_development_sample.csv", development_rows, MAIN_COLUMNS)
    write_csv(SAMPLE_DIR / "system_test_validation_data.csv", validation_rows, MAIN_COLUMNS)
    write_csv(REFERENCE_DIR / "system_test_individual_prediction_cases.csv", build_prediction_rows(), PREDICTION_COLUMNS)
    write_csv(
        REFERENCE_DIR / "system_test_annual_external_indicators.csv",
        build_external_indicator_rows(),
        [
            "indicator_year",
            "indicator_type",
            "indicator_name",
            "geography_level",
            "geography_code",
            "field_code",
            "value",
            "unit",
            "source",
            "source_date",
            "update_date",
            "reliability_level",
            "note",
        ],
    )

    print("Generated system test data")
    print(f"main_rows={len(rows)} development_rows={len(development_rows)} validation_rows={len(validation_rows)}")


if __name__ == "__main__":
    main()
