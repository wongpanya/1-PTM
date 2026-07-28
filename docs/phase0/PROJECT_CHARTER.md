# Phase 0 Project Charter

## Project Name

ODOS Policy Analytics Prototype

## Project Intent

Prototype นี้มีวัตถุประสงค์เพื่อพิสูจน์ว่าข้อมูลผู้รับทุน 1 อำเภอ 1 ทุน สามารถพัฒนาเป็นระบบสนับสนุนนโยบายได้จริง โดยแสดงให้เห็นกระบวนการจากฐานข้อมูลผู้รับทุน ไปสู่ dashboard, analytics, risk score, policy recommendation, external indicators และ governance

## Policy Position

Prototype นี้เป็นระบบสนับสนุนการวิเคราะห์เชิงนโยบาย ไม่ใช่ระบบตัดสินใจอัตโนมัติ และไม่ใช่ระบบ production สำหรับใช้งานจริงทันที

ผลลัพธ์จาก Prototype ต้องตีความเป็น evidence, signal, ranking หรือ recommendation เบื้องต้น เพื่อใช้ประกอบการอภิปรายและนำเสนอของบสนับสนุนสำหรับระบบจริง

## Core Objective

สร้างเว็บ Prototype ที่ใช้ข้อมูลผู้รับทุนจาก project นี้ เพื่อแสดงศักยภาพของระบบสนับสนุนนโยบายผ่าน 7 หน้าหลัก:

1. Overview
2. Data Quality
3. Analytics
4. Risk & Forecast
5. Policy Recommendation
6. External Indicators
7. Governance

## Users

- ผู้บริหารและผู้กำหนดนโยบาย
- นักวิเคราะห์ข้อมูลและนักวิเคราะห์นโยบาย
- เจ้าหน้าที่ดูแลข้อมูลและติดตามผู้รับทุน

## Data Baseline

ข้อมูลตั้งต้นคือไฟล์ใน project นี้ โดยใช้ผลลัพธ์ Phase 1 เป็นฐานข้อมูลกลางสำหรับระบบ:

- `phase1_outputs/odos_policy_analytics_prototype.sqlite`
- `phase1_outputs/data/core_scholarship_dataset.csv`
- `phase1_outputs/data/students.csv`
- `phase1_outputs/data/education.csv`
- `phase1_outputs/data/employment.csv`
- `phase1_outputs/data/data_dictionary.csv`
- `phase1_outputs/data/annual_external_indicators_template.csv`

## Technology Baseline

Prototype จะใช้เทคโนโลยีที่ฟรีหรือมี free tier ก่อน:

- Python
- Streamlit
- Pandas
- Plotly
- SQLite
- Git

## In Scope

- สร้างโครง project และ repository ที่ Codex ทำงานต่อได้
- สร้างเว็บ app แบบ Prototype
- อ่านข้อมูลจาก cleaned dataset หรือ SQLite ที่เตรียมแล้ว
- แสดง dashboard และ analytics จากข้อมูลจริงที่ลดการเปิดเผยข้อมูลส่วนบุคคล
- แสดง data quality และ data readiness
- สร้าง risk score แบบ rule-based หรือ model เบื้องต้นที่อธิบายได้
- สร้าง policy recommendation แบบ decision support
- สร้างหน้า external indicators พร้อม template ข้อมูลเสริมรายปี
- สร้างหน้า governance เพื่อแสดง PII masking, role concept, audit log และ export policy
- เตรียมเอกสารส่งมอบและ roadmap สำหรับ Production System

## Out of Scope

- ระบบ production สำหรับใช้งานจริงระดับองค์กร
- authentication และ authorization เต็มรูปแบบ
- security hardening ระดับ production
- database server กลางพร้อม SLA, monitoring และ backup
- API เชื่อมต่อข้อมูลภายนอกจริง
- ML production pipeline
- automated scholarship allocation decision
- PDPA workflow เต็มรูปแบบ
- การแก้ไขข้อมูลต้นฉบับโดยตรงใน Excel

## Key Decisions

| Decision Area | Phase 0 Decision |
| --- | --- |
| Prototype language | ภาษาไทยเป็นหลัก และใช้คำอังกฤษกำกับคำเทคนิคเมื่อจำเป็น |
| Primary users | ผู้บริหาร, นักวิเคราะห์, เจ้าหน้าที่ข้อมูล |
| Runtime data source | ใช้ฐานข้อมูลกลาง/cleaned CSV จาก Phase 1 เป็นค่าเริ่มต้น |
| Excel upload | ยังไม่เปิดให้ผู้ใช้ทั่วไป upload ในรอบแรก; ถ้ามีให้เป็น admin/dev mode |
| Data type | ใช้ข้อมูลจริงที่ลดการระบุตัวตนและแสดงผลแบบ aggregate เป็นหลัก |
| Deployment target | เตรียมให้ deploy ออนไลน์ได้ด้วย free tier แต่สาธิตในเครื่องได้ระหว่างพัฒนา |
| Recommendation type | Decision support เท่านั้น ไม่ใช่ automatic decision |
| Sensitive data | ห้ามแสดงหรือ export ข้อมูลติดต่อและข้อมูลส่วนบุคคลโดยตรง |

## Success Criteria

Prototype ถือว่าสำเร็จเมื่อสามารถสาธิตได้ว่า:

- ข้อมูลผู้รับทุนถูกจัดระเบียบเป็นฐานข้อมูลกลาง
- ผู้ใช้สามารถดูภาพรวมและ drill-down ข้อมูลสำคัญได้
- ระบบแสดงคุณภาพข้อมูลและข้อจำกัดของข้อมูลได้
- ระบบสร้าง risk score เบื้องต้นพร้อมเหตุผลได้
- ระบบสร้าง policy recommendation เบื้องต้นจากข้อมูลได้
- ระบบรองรับแนวคิดข้อมูลเสริมรายปี
- ระบบมีแนวทาง governance และ PII masking ในระดับ Prototype
- มีเอกสารสำหรับส่งมอบและ roadmap ไป Production System

## Phase 0 Status

Status: Locked for Prototype Development

Phase 0 จะถือว่าเสร็จเมื่อมีไฟล์ต่อไปนี้:

- `PROJECT_SCOPE.md`
- `docs/phase0/PROJECT_CHARTER.md`
- `docs/phase0/ACCEPTANCE_CHECKLIST.md`
- `docs/phase0/DECISION_LOG.md`
