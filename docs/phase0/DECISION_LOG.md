# Phase 0 Decision Log

เอกสารนี้บันทึกการตัดสินใจสำคัญสำหรับ ODOS Policy Analytics Prototype

## Decision 001: Prototype Purpose

Decision: Prototype ใช้เพื่อพิสูจน์ศักยภาพของระบบวิเคราะห์ข้อมูลผู้รับทุนเพื่อสนับสนุนนโยบาย

Rationale: เป้าหมายรอบแรกคือทำให้เห็นภาพระบบและใช้ประกอบการนำเสนอของบสนับสนุน ไม่ใช่ใช้งานจริงเต็มรูปแบบ

Impact: ระบบต้องเน้นความชัดเจน อธิบายได้ และแสดงข้อจำกัดของข้อมูลเสมอ

## Decision 002: Prototype Is Not Production

Decision: Prototype แตกต่างจาก Production System

Rationale: Production System ต้องมีระบบสิทธิ์ ความปลอดภัย ฐานข้อมูลกลางจริง API การเชื่อมโยงข้อมูลภายนอก ML pipeline และ governance เต็มรูปแบบ ซึ่งเกินขอบเขต 2-3 วัน

Impact: Prototype จะใช้ local database, simple app structure และ mock governance ก่อน

## Decision 003: Main Pages

Decision: Prototype ต้องมี 7 หน้าหลัก

Pages:

1. Overview
2. Data Quality
3. Analytics
4. Risk & Forecast
5. Policy Recommendation
6. External Indicators
7. Governance

Rationale: 7 หน้านี้ครอบคลุมฐานข้อมูล Dashboard การวิเคราะห์ ความเสี่ยง ข้อเสนอเชิงนโยบาย ข้อมูลเสริมรายปี และธรรมาภิบาลข้อมูล

Impact: Phase 3-8 ต้องออกแบบ navigation และ feature ให้ยึดตาม 7 หน้านี้

## Decision 004: Language

Decision: ระบบใช้ภาษาไทยเป็นหลัก และใช้คำอังกฤษเมื่อเป็นคำเทคนิคหรือชื่อโมดูล

Examples: Overview, Data Quality, Risk Score, External Indicators, Governance

Rationale: ผู้ใช้หลักเป็นผู้บริหาร เจ้าหน้าที่ และนักวิเคราะห์ในบริบทไทย แต่ทีมพัฒนาและเครื่องมืออาจใช้ศัพท์อังกฤษ

Impact: UI copy ต้องอ่านง่ายแบบไทย แต่ code/module names ใช้ภาษาอังกฤษได้

## Decision 005: Primary Users

Decision: ผู้ใช้หลักมี 3 กลุ่ม

- ผู้บริหารและผู้กำหนดนโยบาย
- นักวิเคราะห์ข้อมูลและนักวิเคราะห์นโยบาย
- เจ้าหน้าที่ดูแลข้อมูลและติดตามผู้รับทุน

Rationale: Prototype ต้องสื่อสารได้ทั้งระดับบริหารและระดับปฏิบัติการ

Impact: Dashboard ต้องมีทั้ง executive summary และรายละเอียดที่ drill-down ได้

## Decision 006: Runtime Data Source

Decision: ระบบรอบแรกใช้ฐานข้อมูลกลางหรือ cleaned CSV จาก Phase 1 เป็น runtime data source

Rationale: การอ่าน Excel ต้นฉบับทุกครั้งจะช้ากว่า ควบคุมคุณภาพข้อมูลยากกว่า และเสี่ยงให้ logic cleaning กระจายอยู่ในหลายจุด

Impact: App ควรอ่านจาก `phase1_outputs/odos_policy_analytics_prototype.sqlite` หรือ `phase1_outputs/data/*.csv`

## Decision 007: Excel Upload

Decision: Prototype รอบแรกไม่เปิด upload ให้ผู้ใช้ทั่วไป

Rationale: upload ต้องมี validation, versioning, overwrite protection และ governance ซึ่งยังไม่จำเป็นสำหรับการสาธิตแรก

Impact: หากต้องมี upload ให้จำกัดเป็น admin/dev mode และไม่ overwrite dataset เดิมโดยตรง

## Decision 008: Data Type and Privacy

Decision: ใช้ข้อมูลจริงที่ลดการระบุตัวตน และแสดงผลแบบ aggregate เป็นหลัก

Rationale: ข้อมูลผู้รับทุนมีข้อมูลส่วนบุคคลและข้อมูลติดตามอาชีพ จึงต้องลดความเสี่ยงในการเปิดเผยข้อมูล

Impact: Dashboard ห้ามแสดงชื่อ เบอร์โทร เลขที่สัญญา ที่อยู่ละเอียด หรือหมายเหตุเจ้าหน้าที่ที่อาจมีข้อมูลอ่อนไหว

## Decision 009: Deployment

Decision: เตรียมระบบให้ deploy ออนไลน์ได้ด้วย free tier แต่ระหว่างพัฒนาสามารถสาธิตในเครื่องได้

Preferred options:

- Streamlit Community Cloud
- Hugging Face Spaces

Rationale: ต้องการทำ Prototype ภายใน 2-3 วันและลดต้นทุนเริ่มต้น

Impact: Technology stack ต้องเรียบง่ายและ reproducible

## Decision 010: Risk and Recommendation

Decision: Risk score และ policy recommendation ต้องอธิบายได้ และเป็น decision support เท่านั้น

Rationale: Prototype ยังไม่มีข้อมูลภายนอกครบถ้วนและยังไม่ได้ผ่านกระบวนการ validation เชิงนโยบายเต็มรูปแบบ

Impact: ทุกคะแนนหรือข้อเสนอควรแสดงเหตุผล ตัวแปรที่ใช้ และข้อจำกัด

## Decision 011: External Indicators

Decision: ข้อมูลภายนอกให้เริ่มจาก template รายปีก่อน

Rationale: ต้นทุนทุน ตลาดแรงงาน GDP SDGs และตัวชี้วัดเศรษฐกิจ/สังคมเปลี่ยนตามปี และแต่ละปีอาจมีข้อมูลไม่เหมือนกัน

Impact: Prototype ต้องมีหน้า External Indicators เพื่อแสดงแนวคิดการกรอก/อัปเดตข้อมูลเสริมรายปี

## Decision 012: Phase 0 Status

Decision: Phase 0 ถูกล็อกสำหรับการพัฒนา Prototype

Required files:

- `PROJECT_SCOPE.md`
- `docs/phase0/PROJECT_CHARTER.md`
- `docs/phase0/ACCEPTANCE_CHECKLIST.md`
- `docs/phase0/DECISION_LOG.md`

Next Phase: Phase 2 - เตรียม Repository ให้ Codex
