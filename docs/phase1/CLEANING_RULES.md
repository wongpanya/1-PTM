# Phase 1 Cleaning Rules

เอกสารนี้ระบุ cleaning rules สำหรับ ODOS Policy Analytics Prototype ระยะที่ 1 โดยแยกเป็นกฎที่เลือกใช้ทันที และกฎ/ข้อมูลที่เลือกชะลอหรือตัดออกจากชุด Development Sample เพื่อความปลอดภัยและความเหมาะสมของ Prototype

## 1. Cleaning Principles

- ไม่แก้ไขไฟล์ Raw Data โดยตรง
- ทุกการแปลงข้อมูลต้องสร้างเป็น derived dataset แยกต่างหาก
- เลือก clean เฉพาะ field ที่จำเป็นต่อ dashboard, data quality, risk และ forecast รอบแรก
- หลีกเลี่ยงการใช้ข้อมูลส่วนบุคคลหรือ free text ที่ระบุตัวตนได้ใน Development Sample
- เก็บค่า raw ที่สำคัญไว้ในฐานกลางบางส่วนเมื่อจำเป็น แต่ไม่ใช้แสดงบน dashboard โดยตรง
- กฎทั้งหมดต้องอธิบายได้และทำซ้ำได้

## 2. Rules Selected for Prototype

| Rule ID | Rule | Applied To | Why Selected |
| --- | --- | --- | --- |
| CLN-001 | ใช้เฉพาะแถวที่มี `ID` | ทุก dataset | แถวที่ไม่มี ID เป็นแถวว่างหรือส่วน format ต่อท้าย ไม่ใช่ record ผู้รับทุนจริง |
| CLN-002 | สร้าง `odos_uid` เช่น `ODOS00001` | ทุก dataset | ใช้เป็นรหัสไม่ระบุตัวตนแทน ID ต้นฉบับและช่วย join ตาราง |
| CLN-003 | normalize whitespace และ newline ในข้อความ | text fields | ลดปัญหาค่าเดียวกันแต่เว้นวรรค/ขึ้นบรรทัดต่างกัน |
| CLN-004 | แปลง error-like values เช่น `#NUM!`, `#VALUE!`, `#REF!` เป็น missing | date/helper fields | ค่าเหล่านี้ไม่ใช่ค่าข้อมูลจริงและทำให้ analytics เพี้ยน |
| CLN-005 | ใช้คอลัมน์วันที่เต็มแทนคอลัมน์ปี/เดือน/วันแยก | study dates, report dates | คอลัมน์ปี/เดือน/วันแยกมี error-like จำนวนมาก จึงไม่เหมาะเป็นแหล่งหลัก |
| CLN-006 | parse GPA เป็น `gpa_numeric` | GPA | ทำให้ใช้วิเคราะห์ผลสัมฤทธิ์ได้ และแยกจากค่า raw ที่สะกดไม่สม่ำเสมอ |
| CLN-007 | parse รายได้เป็น `income_monthly_est` | income | รายได้มีทั้งช่วงและตัวเลขเดี่ยว จึงใช้ค่ากลางช่วงเป็นค่าประมาณสำหรับ analytics |
| CLN-008 | map ความสอดคล้องเป็นระดับ 0-3 | field-job fit, local fit, satisfaction | ทำให้ใช้สร้าง risk score และเปรียบเทียบกลุ่มได้ |
| CLN-009 | map ความต้องการรับราชการเป็น flag 1/0 | wants_government | ใช้เป็นตัวชี้วัด policy interest และทำ dashboard ได้ง่าย |
| CLN-010 | แยกข้อมูลเป็น `students`, `education`, `employment` | core database | ลดความซ้ำซ้อนและแยกหมวดข้อมูลให้ใช้ต่อกับระบบง่ายขึ้น |
| CLN-011 | สร้าง development/validation split แบบ deterministic จาก `odos_uid` | modeling dataset | ทำให้รันซ้ำแล้วได้ผลเดิม และแยกข้อมูลสำหรับตรวจสอบโมเดล |
| CLN-012 | ตัด direct PII/free text ออกจาก Development Sample | sample datasets | ลดความเสี่ยงข้อมูลส่วนบุคคลและเหมาะกับการพัฒนา dashboard/model |

## 3. Fields Selected for Development Sample

เลือก field ที่สนับสนุน dashboard, risk, forecast และ policy recommendation โดยไม่เป็น direct PII

กลุ่มที่เลือกใช้:

- cohort, round, scholarship type
- sex, birth year
- region, province, district, economic corridor
- education status, country, field group, field
- latest degree, GPA numeric, study duration
- employment type, employment detail
- income monthly estimate
- field-job fit and local fit levels
- government work preference
- target variables สำหรับ risk และ forecast

เหตุผล: field เหล่านี้ตอบคำถามเชิงนโยบายได้โดยไม่จำเป็นต้องเปิดเผยชื่อ เบอร์โทร เลขสัญญา หรือที่อยู่ละเอียด

## 4. Fields Excluded from Development Sample

| Field / Field Group | Reason for Exclusion |
| --- | --- |
| contact prefix/name/relationship/phone | direct PII และไม่จำเป็นต่อ dashboard เชิงนโยบาย |
| contract number and document numbers | sensitive administrative identifier |
| detailed address fields | อาจระบุตัวบุคคลหรือสถานที่เฉพาะได้ |
| officer notes and other free-text comments | อาจมีข้อมูลอ่อนไหวหรือข้อมูลส่วนบุคคลที่ไม่ได้จัดโครงสร้าง |
| employer name | อาจใช้ระบุตัวบุคคลเมื่อรวมกับจังหวัด/ตำแหน่ง/สาขา |
| job title | free text และอาจเฉพาะเจาะจงเกินไปในกลุ่มเล็ก |
| school/university names in sample | อาจใช้ระบุตัวบุคคลในบางกลุ่มเล็ก และยังไม่จำเป็นสำหรับ Prototype รอบแรก |
| raw income text | มีรูปแบบไม่สม่ำเสมอและอาจมีข้อความเสริม จึงใช้ `income_monthly_est` แทน |
| raw GPA text | มีรูปแบบไม่สม่ำเสมอ จึงใช้ `gpa_numeric` แทน |

## 5. Rules Deferred to Later Phases

| Deferred Rule | Why Deferred |
| --- | --- |
| Full Thai spelling standardization for all provinces/countries/universities | ต้องตรวจร่วมกับ domain owner เพื่อไม่รวมค่าที่ต่างกันโดยตั้งใจ |
| Geocoding district/province to coordinates | ต้องใช้ external source และอาจต้องตรวจ license/source |
| Full occupation taxonomy mapping | รายละเอียดอาชีพเป็น free text จำนวนมาก ต้องมีนิยามหมวดอาชีพทางการ |
| Advanced outlier treatment for income | ต้องตกลงนิยามรายได้ รายเดือน/รายปี สวัสดิการ และรายได้ช่วงก่อน |
| Imputation for missing GPA/income | อาจทำให้ตีความผิดใน Prototype จึงควรแสดง missingness แทน |
| ML feature engineering ขั้นสูง | ควรรอ Phase 6 หลัง dashboard และ baseline risk score พร้อม |
| Cross-year external indicator matching | ต้องรอข้อมูลต้นทุน ตลาดแรงงาน GDP และ SDGs รายปี |

## 6. Data Quality Caveats

- Records ที่ใช้ได้จาก `ID`: 3,091
- Development Sample: 2,482 records
- Validation Data: 609 records
- GPA numeric ใช้ได้: 949 records
- Income monthly estimate ใช้ได้: 1,256 records
- ข้อมูลรายได้และ GPA ไม่ควรใช้เป็นข้อสรุปแทนทั้งโครงการโดยไม่แสดง missingness
- Recommendation ใน Prototype ต้องแสดงข้อจำกัดของข้อมูลเสมอ

## 7. Review Requirement

ก่อนใช้ Prototype เพื่อเสนอเชิงนโยบาย ควรมีผู้รับรองนิยามข้อมูลตรวจรายการต่อไปนี้:

- นิยามสถานะสำเร็จ/ลาออก/พ้นสภาพ/เกินระยะเวลา
- นิยาม field-job fit และ local fit
- นิยามรายได้และการใช้ค่าประมาณรายเดือน
- นิยามกลุ่มเสี่ยงและ target variables
- รายการข้อมูลที่ห้ามแสดงหรือ export
