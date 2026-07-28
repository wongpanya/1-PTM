# Phase 1 Data Quality Report

## Scope
รายงานนี้สร้างจากไฟล์ `690724 DB_ODOS Students+.xlsx` โดยอ่านชีต `DB_Students` และใช้เฉพาะแถวที่มี `ID` เพื่อสร้างฐานข้อมูลกลางแบบ Prototype

## Core Metrics
- source_file: 690724 DB_ODOS Students+.xlsx
- source_rows_with_id: 3091
- source_columns: 112
- unique_source_id: 3091
- cohorts: 1: 921, 2: 915, 3: 687, 4: 568
- completion_count: 2921
- completion_rate_pct: 94.5
- province_distinct: 79
- district_distinct: 958
- current_country_distinct: 23
- current_field_group_distinct: 11
- employment_type_distinct: 18
- gpa_numeric_available: 949
- income_monthly_est_available: 1256
- field_job_fit_available: 2129
- local_fit_available: 1587

## Prototype Tables
- `students`: ข้อมูลผู้รับทุนเชิงพื้นที่และข้อมูลพื้นฐานที่ไม่ใช้ข้อมูลติดต่อส่วนบุคคล
- `education`: ข้อมูลสถานะการศึกษา ทุน ประเทศ สาขา วุฒิ GPA และระยะเวลาศึกษา
- `employment`: ข้อมูลอาชีพ รายได้โดยประมาณ ความสอดคล้องงานกับสาขา/ท้องถิ่น และความต้องการรับราชการ
- `annual_external_indicators_template`: โครงสร้างสำหรับกรอกข้อมูลเสริมรายปีในระยะถัดไป

## Data Readiness Notes
- ข้อมูลผู้รับทุนที่ใช้ได้: 3091 records
- อัตราสำเร็จการศึกษาจากสถานะโครงการ: 94.5%
- GPA numeric ใช้ได้: 949 records
- รายได้แปลงเป็นค่าประมาณรายเดือนได้: 1256 records
- คอลัมน์วันที่แยกปี/เดือน/วันบางส่วนมีค่า error-like จำนวนมาก จึงควรใช้คอลัมน์วันที่เต็มในการวิเคราะห์เวลา
- Prototype นี้ไม่ export ข้อมูลติดต่อส่วนบุคคล เช่น ชื่อผู้ติดต่อ โทรศัพท์ เลขที่สัญญา และที่อยู่ละเอียด

## Lowest Completeness Fields
- Col 100 `ข้อมูลประวัติการทำงาน รวม`: 0.03%
- Col 18 `เคยรับทุนอื่น ๆ ก่อนรับทุนโครงการ 1 อำเภอ 1 ทุน`: 0.1%
- Col 59 `ระยะ รับทุน คงเหลือ (ปี)`: 0.39%
- Col 79 `ปีที่สำเร็จการ ศึกษา (ป//ด/ว) (ปริญญาเอก)`: 1.1%
- Col 55 `เลขที่หนังสืออนุมัติ สกอ. (สป.อว.) เข้าศึกษา`: 1.33%
- Col 88 `เลขที่ วันลงนาม หนังสือรับรองการปฏิบัติงาน`: 1.75%
- Col 75 `ประเทศที่เลือกศึกษา (ปริญญาเอก)`: 1.81%
- Col 76 `กลุ่มสาขาวิชา (ปริญญาเอก)`: 1.88%
- Col 77 `สาขาวิชา (ปริญญาเอก)`: 1.88%
- Col 78 `มหาวิทยาลัย (ปริญญาเอก)`: 1.88%
- Col 74 `ปีที่สำเร็จการศึกษา (ป//ด/ว) (ปริญญาโท)`: 2.69%
- Col 36 `ปี`: 4.85%
- Col 37 `เดือน`: 4.85%
- Col 38 `วัน`: 4.85%
- Col 35 `วันที่ยุติการศึกษา/ ลาออก (ปี ค.ศ./เดือน/วัน)`: 5.5%