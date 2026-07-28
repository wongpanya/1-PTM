# Data Definition Sign-off

เอกสารนี้ใช้สำหรับให้ผู้เกี่ยวข้องรับรองนิยามข้อมูลก่อนใช้ Prototype เพื่อสาธิตหรือเสนอเชิงนโยบาย

## Project

ODOS Policy Analytics Prototype

## Phase

Phase 1: เตรียมข้อมูล

## Sign-off Status

Current status: Pending data owner/domain owner confirmation

หมายเหตุ: Codex จัดเตรียมเอกสาร นิยามเบื้องต้น และชุดข้อมูลสำหรับตรวจรับแล้ว แต่ไม่สามารถรับรองนิยามเชิงนโยบายแทนเจ้าของข้อมูลหรือผู้เชี่ยวชาญโครงการได้

## Definitions to Confirm

โปรดตรวจและยืนยันรายการต่อไปนี้

| Item | Definition / Scope | Status | Reviewer |
| --- | --- | --- | --- |
| ผู้รับทุนที่นับใน Prototype | record ที่มี `ID` ในชีต `DB_Students` | Pending | |
| Cohort / รุ่น | ใช้คอลัมน์ `รุ่นที่` | Pending | |
| Graduation Success | `project_condition_status = สำเร็จการศึกษา` | Pending | |
| Scholarship Risk | สถานะ ลาออก, พ้นสภาพ, เกินระยะเวลารับทุน, สละสิทธิ์ | Pending | |
| Tracking Risk | อยู่ระหว่างติดตามข้อมูล หรือไม่พบในฐานข้อมูล | Pending | |
| Employment Ready | ภาคเอกชน, ภาครัฐ, รัฐวิสาหกิจ, ธุรกิจส่วนตัว, องค์กรเอกชนเพื่อสาธารณประโยชน์ | Pending | |
| Field-job Fit | map ระดับ ไม่สอดคล้อง=0, น้อย=1, ปานกลาง=2, มาก=3 | Pending | |
| Local Fit | map ระดับ ไม่สอดคล้อง=0, น้อย=1, ปานกลาง=2, มาก=3 | Pending | |
| Income Estimate | รายได้ช่วงใช้ค่ากลางช่วง รายได้ตัวเลขเดี่ยวใช้ค่าตัวเลขนั้น | Pending | |
| GPA Numeric | ใช้ค่าตัวเลข 0-4 หรือแปลงคะแนน 0-100 เป็น 0-4 เมื่อจำเป็น | Pending | |
| PII Exclusion | ไม่แสดงชื่อ เบอร์โทร เลขสัญญา ที่อยู่ละเอียด และ free text อ่อนไหว | Pending | |
| External Indicators | ข้อมูลภายนอกเป็น template รายปี ยังไม่ใช้เป็นข้อสรุปจริง | Pending | |

## Required Reviewers

อย่างน้อยควรมีผู้รับรองจากบทบาทต่อไปนี้

- Data Owner หรือผู้รับผิดชอบฐานข้อมูลผู้รับทุน
- Domain Expert ด้านโครงการทุน
- Policy Analyst หรือผู้ใช้ผลวิเคราะห์เชิงนโยบาย
- Data Governance / PDPA reviewer หากจะเผยแพร่ demo ให้บุคคลภายนอก

## Sign-off Record

| Reviewer Name | Role | Decision | Date | Notes |
| --- | --- | --- | --- | --- |
| | | Pending / Approved / Needs Revision | | |
| | | Pending / Approved / Needs Revision | | |
| | | Pending / Approved / Needs Revision | | |

## Use Restriction Before Sign-off

ก่อนมีผู้รับรองนิยามข้อมูล ผลลัพธ์จาก Prototype ควรใช้เพื่อ:

- ทดลองพัฒนาระบบ
- สาธิตแนวคิด
- ตรวจความพร้อมของข้อมูล
- เตรียมข้อเสนอของบประมาณ

ไม่ควรใช้เพื่อ:

- ตัดสินใจจัดสรรทุนจริง
- ประเมินบุคคลรายคน
- เผยแพร่ต่อสาธารณะโดยไม่ผ่านการตรวจ privacy
- สรุป ROI/SROI อย่างเป็นทางการ
