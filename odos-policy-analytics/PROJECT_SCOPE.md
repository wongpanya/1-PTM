# ODOS Policy Analytics Prototype - Project Scope

## 1. Purpose

Prototype นี้จัดทำขึ้นเพื่อพิสูจน์ว่า "ข้อมูลผู้รับทุน 1 อำเภอ 1 ทุน" สามารถพัฒนาเป็นระบบสนับสนุนนโยบายได้จริง โดยใช้ข้อมูลใน project นี้เป็นฐานตั้งต้น และแสดงให้เห็นศักยภาพของระบบในด้าน dashboard, data quality, analytics, risk/forecast, policy recommendation, external indicators และ governance

Prototype นี้ไม่ใช่ Production System และไม่ใช่ระบบสำหรับตัดสินใจจัดสรรทุนอัตโนมัติในทันที ผลลัพธ์ของระบบต้องใช้เพื่อสนับสนุนการวิเคราะห์ การอภิปราย และการจัดทำข้อเสนอเชิงนโยบายเท่านั้น

## 2. Prototype vs Production

### Prototype Scope

- ใช้ข้อมูลเท่าที่มีใน project เป็นหลัก
- ใช้ฐานข้อมูลกลางแบบ local/prototype เช่น SQLite และ CSV
- สร้าง web dashboard เพื่อสาธิตแนวคิด
- พัฒนา risk score และ recommendation แบบเบื้องต้นที่อธิบายได้
- มี template สำหรับข้อมูลเสริมรายปี
- มี governance mockup เช่น PII masking, role concept และ audit log เบื้องต้น
- ใช้เครื่องมือฟรีหรือ free tier ก่อน

### Out of Scope for Prototype

- ระบบ production สำหรับใช้งานจริงระดับองค์กร
- authentication/authorization เต็มรูปแบบ
- security hardening ระดับ production
- database server กลางที่มี backup, monitoring, SLA
- machine learning production pipeline
- API เชื่อมโยงข้อมูลภายนอกอัตโนมัติ
- การตัดสินใจจัดสรรทุนอัตโนมัติ
- PDPA workflow เต็มรูปแบบ

## 3. Primary Users

Prototype ออกแบบเพื่อผู้ใช้หลัก 3 กลุ่ม

- ผู้บริหารและผู้กำหนดนโยบาย: ดูภาพรวม ผลลัพธ์ และข้อเสนอเชิงนโยบาย
- นักวิเคราะห์ข้อมูล/นโยบาย: สำรวจข้อมูล เปรียบเทียบมิติ และตรวจสอบเหตุผลของ insight
- เจ้าหน้าที่ดูแลข้อมูล: ตรวจคุณภาพข้อมูลและเตรียมข้อมูลสำหรับการวิเคราะห์

## 4. Initial Language Decision

ระบบ Prototype รอบแรกใช้ภาษาไทยเป็นหลัก และสามารถใช้คำอังกฤษกำกับชื่อโมดูลหรือคำเทคนิคเมื่อช่วยให้สื่อสารกับทีมพัฒนาได้ชัดเจน เช่น Overview, Data Quality, Risk Score, External Indicators

## 5. System Pages

Prototype ต้องมี 7 หน้าหลัก

1. Overview
2. Data Quality
3. Analytics
4. Risk & Forecast
5. Policy Recommendation
6. External Indicators
7. Governance

### 5.1 Overview

เป้าหมาย: แสดงภาพรวมผู้รับทุนและผลลัพธ์สำคัญของโครงการ

เนื้อหาหลัก:

- จำนวนผู้รับทุนทั้งหมด
- จำนวนผู้รับทุนตามรุ่น
- จำนวนตามภูมิภาค จังหวัด อำเภอ
- สถานะการศึกษาและสถานะโครงการ
- ประเทศ สาขา และกลุ่มสาขาวิชา
- อาชีพหลังสำเร็จการศึกษา

### 5.2 Data Quality

เป้าหมาย: แสดงความพร้อมของข้อมูลและช่องว่างที่ต้องปรับปรุง

เนื้อหาหลัก:

- completeness ของ field สำคัญ
- จำนวนค่าว่าง
- จำนวนค่าผิดรูปแบบหรือ error-like values
- field ที่พร้อมใช้กับ analytics
- field ที่ควรแก้ไขก่อนใช้กับ model
- data dictionary

### 5.3 Analytics

เป้าหมาย: วิเคราะห์ข้อมูลเชิงพรรณนาและวินิจฉัย

เนื้อหาหลัก:

- completion rate
- dropout / termination / over-duration
- analysis by cohort, province, region, country, field group
- employment type
- income distribution
- field-job fit
- local fit
- government work preference

### 5.4 Risk & Forecast

เป้าหมาย: สาธิตการให้คะแนนความเสี่ยงและการพยากรณ์เบื้องต้น

เนื้อหาหลัก:

- Scholarship Risk Score
- Graduation Success indicator
- Tracking Risk
- Field-job mismatch risk
- Local mismatch risk
- คำอธิบายเหตุผลของคะแนน

หมายเหตุ: ระยะ Prototype ควรใช้ rule-based score หรือ model เบื้องต้นที่อธิบายได้ก่อน

### 5.5 Policy Recommendation

เป้าหมาย: แปลงผลวิเคราะห์เป็นข้อเสนอเชิงนโยบาย

เนื้อหาหลัก:

- สาขาที่ควรพิจารณาสนับสนุน
- พื้นที่ที่ควรพิจารณา
- กลุ่มที่ควรติดตาม
- ประเทศ/สาขาที่มีผลลัพธ์ดีหรือมีความเสี่ยง
- ข้อเสนอพร้อมเหตุผลและหลักฐานจากข้อมูล

หมายเหตุ: ข้อเสนอใน Prototype เป็น decision support ไม่ใช่ automatic decision

### 5.6 External Indicators

เป้าหมาย: รองรับข้อมูลภายนอกที่เปลี่ยนตามปี

เนื้อหาหลัก:

- template กรอกข้อมูลต้นทุนทุน
- template ข้อมูลตลาดแรงงาน
- template ข้อมูลรายได้เฉลี่ย
- template ข้อมูล GDP/ตัวชี้วัดจังหวัด
- template ข้อมูล SDGs หรือ policy priority
- readiness score สำหรับ ROI/SROI, workforce demand และ national impact

### 5.7 Governance

เป้าหมาย: แสดงแนวทางจัดการข้อมูลส่วนบุคคลและธรรมาภิบาลข้อมูล

เนื้อหาหลัก:

- PII masking concept
- role concept เช่น Admin, Analyst, Viewer
- audit log mockup
- data export policy
- data use notice
- รายการข้อมูลที่ห้ามแสดงหรือห้าม export

## 6. Input Data

ข้อมูลนำเข้าหลักสำหรับ Prototype

- `690724 DB_ODOS Students+.xlsx`
- ชีต `DB_Students`
- ชีต `Remark`

ผลลัพธ์ Phase 1 ที่ใช้ต่อ

- `phase1_outputs/odos_policy_analytics_prototype.sqlite`
- `phase1_outputs/data/core_scholarship_dataset.csv`
- `phase1_outputs/data/students.csv`
- `phase1_outputs/data/education.csv`
- `phase1_outputs/data/employment.csv`
- `phase1_outputs/data/data_dictionary.csv`
- `phase1_outputs/data/annual_external_indicators_template.csv`

ระบบรอบแรกควรอ่านจากฐานข้อมูลกลางหรือ cleaned CSV ที่ Phase 1 สร้างแล้ว ไม่ควรอ่าน Excel ต้นฉบับทุกครั้งใน runtime ของ web app ยกเว้นในหน้า import/pipeline ที่ออกแบบไว้เฉพาะ

## 7. Upload Policy

Prototype รอบแรกไม่จำเป็นต้องเปิดให้ผู้ใช้ทั่วไป upload ไฟล์ใหม่

แนวทางที่แนะนำ:

- ใช้ฐานข้อมูลกลางที่เตรียมแล้วเป็น default dataset
- หากมี upload feature ให้จำกัดเป็น admin/dev mode เท่านั้น
- upload ใหม่ต้องผ่าน validation และไม่ overwrite dataset เดิมโดยตรง

## 8. Data Privacy and Display Rules

Prototype ใช้ข้อมูลจริงที่ผ่านการลดการระบุตัวตนเท่าที่ทำได้ในระดับระบบต้นแบบ

ข้อมูลที่ห้ามแสดงบน dashboard และห้าม export ใน Prototype:

- ชื่อ-สกุลผู้ติดต่อ
- หมายเลขโทรศัพท์
- เลขที่สัญญารับทุน
- เลขที่หนังสือหรือเอกสารรับรอง
- ที่อยู่ละเอียด เช่น บ้านเลขที่ หมู่ที่ ตำบล ถนน รหัสไปรษณีย์
- หมายเหตุเจ้าหน้าที่ที่อาจมีข้อมูลอ่อนไหว

ข้อมูลที่ควรแสดง:

- ข้อมูลรวมระดับ cohort, province, region, country, field group, status และ employment type
- รหัสผู้รับทุนแบบไม่ระบุตัวตน เช่น `odos_uid`
- metric รวม เช่น count, rate, median, average, score

## 9. Core Metrics

ตัวชี้วัดหลักของ Prototype

- total scholarship recipients
- recipients by cohort
- recipients by province/region/district
- completion count and completion rate
- dropout/termination/over-duration count
- current country distribution
- field group distribution
- employment type distribution
- income availability and income estimate
- GPA availability and GPA summary
- field-job fit
- local fit
- government work preference
- data completeness score
- risk score
- policy recommendation ranking

## 10. Agents / System Modules

Prototype จะออกแบบ agents เป็น system modules ก่อน

- Data Steward Agent: ตรวจคุณภาพข้อมูลและเสนอ cleaning issues
- Analytics Agent: สรุป descriptive/diagnostic analytics
- Risk Prediction Agent: คำนวณ risk score และอธิบายเหตุผล
- Policy Recommendation Agent: สร้างข้อเสนอเชิงนโยบายจากข้อมูล
- External Indicator Agent: จัดการ template ข้อมูลเสริมรายปี
- Governance Agent: จัดการ PII masking, role concept และ audit log
- Technical Agent: ดูแล reproducibility, deployment, database, security, monitoring และ support

Agent ทุกบทบาททำงานแบบ Human-in-the-loop การรับรอง Label กฎความเสี่ยง น้ำหนักเชิงนโยบาย และข้อกำกับข้อมูลต้องทำโดยผู้รับผิดชอบที่เป็นมนุษย์

## 11. Technology Direction

เทคโนโลยีที่แนะนำสำหรับ Prototype

- Web app: Streamlit
- Data processing: Python + Pandas
- Database: SQLite
- Visualization: Plotly
- Deployment: Streamlit Community Cloud หรือ Hugging Face Spaces
- Version control: Git

หลักการเลือกเทคโนโลยี:

- ฟรีหรือมี free tier
- deploy ง่าย
- ใช้ข้อมูล local/CSV/SQLite ได้
- เหมาะกับ prototype ภายใน 2-3 วัน
- สามารถต่อยอดเป็น production ได้ภายหลัง

## 12. Prototype Phases

| Phase | Goal | Main Outputs |
| ----- | ---- | ------------ |
| 0 | Lock prototype scope | `PROJECT_SCOPE.md`, acceptance criteria |
| 1 | Prepare data | Data dictionary, cleaning rules, sample/cleaned data |
| 2 | Prepare repository for Codex | Git repository, `AGENTS.md`, project structure |
| 3 | Build app skeleton | Streamlit app, navigation, database access |
| 4 | Build data pipeline | Import, cleaning, validation, data quality |
| 5 | Build dashboard and analytics | Overview, Data Quality, Analytics pages |
| 6 | Build risk, forecast and policy | Risk Score, Graduation Success, Recommendation |
| 7 | Add external indicators and governance | Annual template, PII masking, audit log |
| 8 | Test, deploy and hand over | Web demo, tests, documentation, roadmap |
| 9 | Expand to production | Database server, authentication, ML, API |

## 13. Acceptance Criteria

Prototype Phase 0-8 ถือว่าผ่านเมื่อมีผลลัพธ์ดังนี้

- มีเอกสาร scope ที่ล็อกขอบเขตและข้อจำกัดชัดเจน
- มีฐานข้อมูลกลางหรือ cleaned dataset ที่ใช้รันระบบได้
- มี web app ที่เปิดได้และมี 7 หน้าหลัก
- Overview แสดง metric หลักได้ถูกต้อง
- Data Quality แสดง completeness และ field readiness ได้
- Analytics แสดงผลตาม cohort, province, country, field และ employment ได้
- Risk & Forecast มี risk score เบื้องต้นและคำอธิบายที่มา
- Policy Recommendation แสดงข้อเสนอเชิงนโยบายพร้อมเหตุผลจากข้อมูล
- External Indicators มี template สำหรับกรอกข้อมูลรายปี
- Governance แสดงแนวทาง PII masking, role concept และ audit log
- มีเอกสาร README หรือคู่มือใช้งานเบื้องต้น
- มี roadmap สำหรับต่อยอดเป็น production

## 14. Phase 0 Completion Criteria

Phase 0 ถือว่าผ่านเมื่อ

- `PROJECT_SCOPE.md` ถูกสร้างแล้ว
- ขอบเขต Prototype และ out-of-scope ชัดเจน
- รายการ 7 หน้าหลักถูกยืนยัน
- input data และ privacy rules ถูกระบุ
- acceptance criteria ถูกระบุ
- ยืนยันร่วมกันว่า Prototype เป็นระบบสนับสนุนการวิเคราะห์เชิงนโยบาย ไม่ใช่ระบบตัดสินใจอัตโนมัติ

## 15. Key Constraints

- เวลาดำเนินการ Prototype เป้าหมาย 2-3 วัน
- ใช้ข้อมูลที่มีใน project ก่อน
- ไม่เชื่อมข้อมูลภายนอกจริงในรอบแรก ยกเว้น template/mock data
- ไม่เปิดเผยข้อมูลส่วนบุคคลบน dashboard
- recommendation ต้องอธิบายได้
- ผลวิเคราะห์ต้องแสดงข้อจำกัดของข้อมูลเสมอ

## 16. Next Step

หลังยืนยัน `PROJECT_SCOPE.md` แล้ว ให้ดำเนินการ Phase 2 คือเตรียม repository สำหรับ Codex โดยจัดโครงสร้าง project, สร้าง `AGENTS.md`, ระบุคำสั่งรันระบบ, กำหนด coding conventions และเตรียม Streamlit app skeleton สำหรับ Phase 3
