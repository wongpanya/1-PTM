# Phase 1 Outputs: ODOS Core Scholarship Database

ผลลัพธ์ชุดนี้เป็นฐานข้อมูลกลางระดับ Prototype สำหรับระบบ ODOS Policy Analytics Platform
สร้างจากไฟล์ต้นฉบับ `690724 DB_ODOS Students+.xlsx` โดยไม่แก้ไขไฟล์ต้นฉบับ

## Output Files

- `odos_policy_analytics_prototype.sqlite`
  - ฐานข้อมูล SQLite สำหรับใช้ต่อกับเว็บ Prototype, dashboard หรือ analytics notebook

- `data/core_scholarship_dataset.csv`
  - ตารางรวมแบบ denormalized สำหรับ dashboard ที่ต้องการอ่านไฟล์เดียว

- `data/students.csv`
  - ข้อมูลพื้นฐานผู้รับทุนและพื้นที่ เช่น รุ่น เพศ จังหวัด อำเภอ ภูมิภาค ประเทศ/เขตเศรษฐกิจ

- `data/education.csv`
  - ข้อมูลสถานะการศึกษา ประเทศ สาขา มหาวิทยาลัย สถานะโครงการ วุฒิ GPA และระยะเวลาศึกษา

- `data/employment.csv`
  - ข้อมูลอาชีพ รายได้โดยประมาณ ความสอดคล้องงานกับสาขา/ท้องถิ่น และความต้องการรับราชการ

- `data/data_dictionary.csv`
  - รายการคอลัมน์จากไฟล์ต้นฉบับ 112 คอลัมน์ พร้อม mapped field, หมวดข้อมูล, completeness และตัวอย่างค่าที่พบ

- `data/data_quality_summary.csv`
  - metric คุณภาพข้อมูลระดับภาพรวม

- `data/annual_external_indicators_template.csv`
  - template สำหรับกรอกข้อมูลเสริมรายปีในระยะถัดไป เช่น ต้นทุนทุน ตลาดแรงงาน และตัวชี้วัดพื้นที่

- `reports/phase1_data_quality_report.md`
  - รายงานคุณภาพข้อมูลแบบอ่านง่าย

- `reports/phase1_schema.json`
  - schema ของตารางและ field ที่สร้างในฐานข้อมูล Prototype

## SQLite Tables

- `students`
- `education`
- `employment`
- `core_scholarship_dataset`
- `data_dictionary`
- `data_quality_summary`
- `annual_external_indicators_template`

## Data Governance Notes

Prototype นี้หลีกเลี่ยงการ export ข้อมูลติดต่อส่วนบุคคลโดยตรง เช่น ชื่อผู้ติดต่อ เบอร์โทรศัพท์ เลขที่สัญญา และที่อยู่ละเอียด
การนำเสนอเชิงนโยบายควรใช้ข้อมูลแบบ aggregate เป็นหลัก เช่น จำนวน อัตรา ค่าเฉลี่ย และ ranking ตามกลุ่ม

## Verified Counts

- records with source ID: 3,091
- data dictionary fields: 112
- completion count: 2,921
- parsed monthly income records: 1,256
- parsed GPA records: 949

## Next Step

ระยะที่ 2 ควรนำ SQLite/CSV ชุดนี้ไปสร้าง web dashboard และหน้า data quality ก่อน
จากนั้นค่อยเพิ่มโมดูล risk score, policy recommendation และหน้ากรอก annual external indicators
