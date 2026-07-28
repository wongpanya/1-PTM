# Phase 1 Target Variables for Risk and Forecast

เอกสารนี้ระบุตัวแปรเป้าหมายสำหรับใช้ต่อในหน้า Risk & Forecast และโมดูล Policy Recommendation ของ Prototype

## 1. Target Variables Created in Phase 1

| Target Variable | Type | Definition | Positive Class Means | Readiness |
| --- | --- | --- | --- | --- |
| `target_graduation_success` | binary | `project_condition_status = สำเร็จการศึกษา` | ผู้รับทุนสำเร็จการศึกษา | Ready |
| `target_scholarship_risk` | binary | `project_condition_status` อยู่ในกลุ่ม ลาออก, พ้นสภาพ, เกินระยะเวลารับทุน, สละสิทธิ์ | ผู้รับทุนมีเหตุการณ์เสี่ยงตามสถานะโครงการ | Ready |
| `target_tracking_risk` | binary | `employment_type` มีค่าอยู่ระหว่างติดตามข้อมูล หรือ `current_status` ระบุไม่พบในฐานข้อมูล | มีความเสี่ยงด้านการติดตามข้อมูลหลังสำเร็จ | Prototype-ready |
| `target_employment_ready` | binary | `employment_type` อยู่ในกลุ่ม ภาคเอกชน, ภาครัฐ, รัฐวิสาหกิจ, ธุรกิจส่วนตัว, องค์กรเอกชนเพื่อสาธารณประโยชน์ | มีข้อมูลสถานะประกอบอาชีพเชิงบวก | Prototype-ready |
| `target_field_mismatch` | binary | `field_job_fit_level` เป็น 0 หรือ 1 | งานไม่สอดคล้องหรือสอดคล้องน้อยกับสาขา | Prototype-ready |
| `target_local_mismatch` | binary | `local_fit_level` เป็น 0 หรือ 1 | งานไม่สอดคล้องหรือสอดคล้องน้อยกับท้องถิ่น | Prototype-ready |

## 2. Targets Recommended for Phase 6

### 2.1 Graduation Success

Primary target: `target_graduation_success`

Use case:

- คาดการณ์โอกาสสำเร็จการศึกษา
- วิเคราะห์ปัจจัยที่สัมพันธ์กับความสำเร็จ เช่น cohort, country, field group, study duration

Important caveat:

- ค่า target นี้เกิดจากสถานะปัจจุบัน ไม่ใช่ข้อมูล longitudinal แบบ real-time

### 2.2 Scholarship Risk

Primary target: `target_scholarship_risk`

Use case:

- ระบุกลุ่มที่มีความเสี่ยงลาออก พ้นสภาพ เกินระยะเวลา หรือสละสิทธิ์
- ใช้ทำ early warning prototype

Important caveat:

- Prototype ใช้ historical status ไม่ใช่การแจ้งเตือนสด

### 2.3 Tracking Risk

Primary target: `target_tracking_risk`

Use case:

- ระบุกลุ่มที่ข้อมูลหลังสำเร็จยังติดตามไม่ได้
- ช่วยออกแบบ workflow ติดตามข้อมูลเพิ่มเติม

Important caveat:

- ต้องตรวจนิยามร่วมกับเจ้าหน้าที่ เพราะคำว่า "อยู่ระหว่างติดตามข้อมูล" อาจมีหลายสถานการณ์

### 2.4 Employment Readiness

Primary target: `target_employment_ready`

Use case:

- วิเคราะห์ผลลัพธ์ด้านการมีงานทำ
- ใช้ประกอบ Employment & Income Forecast เบื้องต้น

Important caveat:

- ไม่เท่ากับการมีงานทำตามนิยามทางสถิติแรงงานอย่างเป็นทางการ

### 2.5 Field Mismatch Risk

Primary target: `target_field_mismatch`

Use case:

- วิเคราะห์ความเสี่ยงเรียนจบแล้วทำงานไม่ตรงสาขา
- ใช้ประกอบ Field Recommendation และ Policy Recommendation

Important caveat:

- ระดับความสอดคล้องเป็นข้อมูลจัดหมวดจากการตรวจสอบเดิม ต้องยืนยันนิยามกับ domain owner

### 2.6 Local Mismatch Risk

Primary target: `target_local_mismatch`

Use case:

- วิเคราะห์ความเสี่ยงที่งานไม่สอดคล้องกับท้องถิ่นหรือเป้าหมายพื้นที่
- ใช้ประกอบ Area-based Allocation

Important caveat:

- การตีความ "สอดคล้องท้องถิ่น" ต้องมีนิยามเชิงนโยบายประกอบ

## 3. Forecast Targets Not Ready Yet

| Forecast Target | Why Not Ready | Required Additional Data |
| --- | --- | --- |
| ROI Forecast | ยังไม่มีต้นทุนทุนรายคน/รายประเทศ/รายปีครบ | scholarship cost, tuition, living cost, travel, exchange rate |
| SROI Forecast | ยังไม่มี social value proxy และ weight อย่างเป็นทางการ | social outcome indicators, SDGs, community impact, valuation rules |
| Future Workforce Demand | ยังไม่มี demand ตลาดแรงงานรายสาขา/พื้นที่/ปี | labor market demand, shortage occupation, industry growth |
| National Impact Forecast | ยังไม่มี linkage กับ GDP, productivity, innovation output | GDP, sector contribution, patents, startups, public sector impact |
| Future Leadership Potential | ข้อมูลตำแหน่งผู้นำ/งานวิจัย/สิทธิบัตรยังไม่เป็นระบบ | leadership role, research output, patents, awards, organization level |

## 4. Target Variable Governance

- Target variables ใน Prototype เป็นนิยามเชิงปฏิบัติการเบื้องต้น
- ต้องมีผู้รับรองนิยามก่อนนำไปใช้ประกอบข้อเสนอเชิงนโยบายอย่างเป็นทางการ
- ทุกหน้า dashboard/model ต้องแสดงนิยาม target และข้อจำกัดอย่างย่อ
- ไม่ควรใช้ target variables เพื่อจัดสรรทุนอัตโนมัติ

## 5. Data Files

Target variables ถูกสร้างในไฟล์:

- `phase1_outputs/samples/development_sample.csv`
- `phase1_outputs/samples/validation_data.csv`
- `phase1_outputs/samples/modeling_dataset_no_pii.csv`
