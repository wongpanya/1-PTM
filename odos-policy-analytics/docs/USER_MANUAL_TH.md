# คู่มือการใช้งานระบบ ODOS Policy Analytics Prototype

เอกสารนี้เป็นคู่มือการใช้งานระบบต้นแบบ ODOS Policy Analytics Prototype สำหรับการสาธิต วิเคราะห์ และติดตามข้อมูลผู้รับทุนเชิงนโยบาย ระบบนี้ยังไม่ใช่ Production System และไม่ใช่ระบบตัดสินใจจัดสรรทุนอัตโนมัติ ทุกผลลัพธ์ต้องใช้ประกอบการพิจารณาของผู้เชี่ยวชาญและผู้มีอำนาจอนุมัติเท่านั้น

## 1. ภาพรวมระบบ

ODOS Policy Analytics Prototype เป็นเว็บแอป Streamlit ที่ใช้ข้อมูลตัวอย่างแบบไม่มีข้อมูลระบุตัวบุคคลโดยตรง เพื่อแสดงภาพรวมผู้รับทุน คุณภาพข้อมูล การวิเคราะห์ผลลัพธ์ ความเสี่ยง ข้อเสนอเชิงนโยบาย ตัวชี้วัดภายนอก และธรรมาภิบาลข้อมูล

ระบบประกอบด้วยหน้าหลักดังนี้

1. Prototype Application
2. Overview
3. Data Quality
4. Analytics
5. Risk Forecast
6. Policy Recommendation
7. External Indicators
8. Governance
9. Help Documentation

ข้อมูลหลักของระบบมาจากไฟล์ตัวอย่างใน `data/sample/` และผลลัพธ์ที่ผ่าน pipeline ใน `data/processed/` โดยข้อมูลดิบจริงต้องอยู่ภายนอก repository และไม่ควรถูก commit หรืออัปโหลดไปยัง public hosting

## 2. กลุ่มผู้ใช้งานและสิทธิ์

ระบบใช้ Role Mockup เพื่อจำลองสิทธิ์การใช้งาน ยังไม่ใช่ระบบยืนยันตัวตนจริง

| Role | ใช้งานหลัก | สิทธิ์สำคัญ |
| --- | --- | --- |
| Admin | ผู้ดูแลระบบต้นแบบและข้อมูล | นำเข้า external indicator, export aggregate, ดู audit/export log |
| Analyst | นักวิเคราะห์ข้อมูล | ดู dashboard และ export aggregate |
| Viewer | ผู้ชมผลลัพธ์รวม | ดูผลลัพธ์รวมเท่านั้น ไม่สามารถ import/export หรือดู log |
| CaseOfficer | เจ้าหน้าที่สร้างคำขอพยากรณ์รายกรณี | สร้างคำขอประเมินรายกรณีใน Risk Forecast |
| HumanReviewer | ผู้ตรวจทานผลรายกรณี | ตรวจข้อมูลและผลโมเดล ยืนยัน override หรือขอข้อมูลเพิ่ม |
| DomainApprover | ผู้เชี่ยวชาญอนุมัติแผนช่วยเหลือ | อนุมัติหรือไม่อนุมัติแผนหลังผ่าน Human Review |
| ModelOwner | ผู้ดูแลโมเดล | ตรวจ Model registry, calibration, threshold และ export aggregate |
| DPOAuditor | ผู้ตรวจด้านข้อมูลส่วนบุคคล | ตรวจวัตถุประสงค์ สิทธิ์การเข้าถึง และ audit trail |

ข้อควรจำ: Role ใน Prototype เป็นตัวเลือกบนหน้าเว็บ ไม่ใช่ระบบ login จริง หากนำไปใช้จริงต้องเพิ่ม authentication, authorization, audit retention, encryption และกระบวนการ PDPA ให้ครบถ้วน

## 3. การเริ่มใช้งานระบบ

### 3.1 ติดตั้งและเปิดระบบด้วย command line

เปิด PowerShell ที่โฟลเดอร์ `odos-policy-analytics` แล้วรันคำสั่งต่อไปนี้

```powershell
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
streamlit run app.py
```

หลังจากรันคำสั่งสุดท้าย Streamlit จะแสดง URL สำหรับเปิดเว็บแอปใน browser เช่น `http://localhost:8501`

### 3.2 เปิดระบบด้วย Windows Launcher

หากต้องการใช้ปุ่มลัด ให้ double-click ไฟล์ต่อไปนี้

```text
RUN_ODOS_MENU.bat
```

หรือใช้เมนูย่อยใน `odos-policy-analytics/launchers/` เช่น

| Launcher | ใช้ทำอะไร |
| --- | --- |
| `03_phase3_run_app.bat` | เปิด Streamlit app |
| `04_phase4_data_pipeline.bat` | รัน data pipeline จาก raw Excel ภายนอก repo |
| `05_phase5_dashboard.bat` | refresh ข้อมูลและเปิดหน้า dashboard |
| `06_phase6_risk_policy.bat` | รันทดสอบและเปิดหน้า risk/policy |
| `07_phase7_governance.bat` | รันทดสอบ privacy และเปิดหน้า governance |
| `08_phase8_acceptance.bat` | รัน acceptance suite สำหรับส่งมอบ Prototype |

### 3.3 ตรวจความพร้อมก่อนใช้งาน

ให้รันคำสั่งเหล่านี้เมื่อต้องการตรวจระบบแบบครบชุด

```powershell
python scripts/run_unit_tests.py
python scripts/validate_data.py
python scripts/privacy_check.py
python scripts/phase8_acceptance.py
```

หากคำสั่งใดล้มเหลว ควรแก้ไขก่อนใช้ผลวิเคราะห์ประกอบการประชุมหรือส่งมอบ

## 4. วิธีใช้หน้าหลัก Prototype Application

หน้าหลักใช้ตรวจสถานะระบบและนำทางไปยังระบบย่อย

ขั้นตอนใช้งาน

1. เปิดแอปด้วย `streamlit run app.py`
2. ดูตัวเลขสถานะฐานข้อมูลกลาง เช่น จำนวนระเบียนผู้รับทุน จำนวนระเบียนที่ import และจำนวน audit events
3. ตรวจสถานะตารางฐานข้อมูลที่แสดงบนหน้า
4. ใช้เมนูด้านซ้ายเพื่อเปิดหน้า Overview, Data Quality, Analytics, Risk Forecast, Policy Recommendation, External Indicators, Governance หรือ Help Documentation

การอ่านผล

- หากฐานข้อมูลพร้อม ระบบจะแสดงจำนวน record และสถานะตาราง
- หากฐานข้อมูลยังไม่พร้อม ให้รัน import/build database หรือ launcher ที่เกี่ยวข้องก่อน
- ข้อความ warning บนหน้าเป็นข้อเตือนว่า Prototype ใช้เพื่อสาธิตและต้องให้ผู้เชี่ยวชาญตรวจสอบก่อนใช้งานจริง

## 5. คู่มือระบบ Overview

### 5.1 วัตถุประสงค์

Overview ใช้ดูภาพรวมโครงการในระดับ aggregate เช่น จำนวนผู้รับทุน ผลลัพธ์การศึกษา การมีงานทำ ความเสี่ยงทุน รายได้ ความสอดคล้องงานกับสาขา และช่องว่างการติดตามข้อมูล

### 5.2 ตัวกรองที่ใช้ได้

ตัวกรองอยู่ที่ sidebar ด้านซ้าย

- ปีวิเคราะห์
- รุ่น
- ภูมิภาค
- จังหวัด
- อำเภอ
- ประเทศ
- กลุ่มสาขา
- สาขารายละเอียด
- มหาวิทยาลัยมาตรฐาน
- รหัสภาคส่วนผู้จ้าง
- สิทธิ์สำหรับ Export: Analyst, Admin, Viewer

เมื่อเลือกตัวกรอง ค่า KPI และกราฟทั้งหมดจะปรับตามข้อมูลที่กรองทันที หากไม่พบข้อมูล ระบบจะแสดง warning ให้ลดเงื่อนไขหรือเลือกตัวกรองใหม่

### 5.3 KPI สำคัญบนหน้า Overview

| KPI | ความหมาย |
| --- | --- |
| ผู้รับทุนทั้งหมด | จำนวน record ในชุดข้อมูลที่ผ่านตัวกรอง |
| เสี่ยงติดตามไม่ครบ | จำนวนและสัดส่วน record ที่ข้อมูล follow-up ไม่ครบ |
| ข้อมูลรายได้ | จำนวน record ที่มีข้อมูลรายได้ใช้วิเคราะห์ได้ |
| สำเร็จการศึกษา | จำนวนและอัตราผู้ที่สำเร็จการศึกษา |
| มีงานทำ | จำนวนและอัตราผู้ที่มีข้อมูลว่ามีงานทำ |
| ออกจากทุนกลางคัน | อัตรา dropout ตามนิยาม Prototype |
| ยุติทุน | อัตราการยุติทุน |
| ความเสี่ยงทุน | อัตราผู้รับทุนที่เข้าเกณฑ์ความเสี่ยง |
| งานตรงสาขา | สัดส่วนผู้มีงานที่สอดคล้องกับสาขา |
| งานสอดคล้องท้องถิ่น | สัดส่วนงานที่สอดคล้องกับการพัฒนาพื้นที่ |

### 5.4 แท็บการวิเคราะห์

| แท็บ | ใช้ดูอะไร |
| --- | --- |
| ผู้รับทุน | จำนวนผู้รับทุนตามรุ่น เพศ และภูมิภาค |
| การศึกษา | สถานะตามเงื่อนไขโครงการ ประเทศ กลุ่มสาขา และมหาวิทยาลัยที่ normalize แล้ว |
| ผลลัพธ์หลังทุน | รายได้ ประเภทอาชีพ ภาคส่วนผู้จ้าง งานตรงสาขา และ local fit |
| พื้นที่ | ผลสำเร็จรายจังหวัด และจำนวนตามจังหวัด/อำเภอ |
| แนวโน้มตามรุ่น | แนวโน้ม completion, employment, scholarship risk และ tracking gap |
| ข้อมูลติดตามขาด | ความครบถ้วนข้อมูลติดตามตามมิติที่เลือก |

### 5.5 การ Export

1. เลือกตัวกรองให้ตรงกับประชากรที่ต้องการ
2. เลือกสิทธิ์สำหรับ Export เป็น Analyst หรือ Admin
3. กด `Export Overview Aggregate CSV`
4. ระบบจะส่งออกเฉพาะข้อมูล aggregate และบันทึก export log หลังจากกดปุ่ม download

Viewer ไม่มีสิทธิ์ export

### 5.6 ข้อควรระวัง

- ผลลัพธ์รายกลุ่มที่มีจำนวนน้อยกว่า minimum group size จะถูกปกปิดหรือไม่แสดง
- รายได้เป็นสถิติ aggregate และตัดค่าที่อยู่นอกช่วง validation
- University standardization เป็นการ normalize ข้อความ ยังไม่ใช่รหัสสถาบันทางการ

## 6. คู่มือระบบ Data Quality

### 6.1 วัตถุประสงค์

Data Quality ใช้ตรวจความพร้อมของข้อมูลก่อนนำไปวิเคราะห์ สร้าง dashboard วางนโยบาย หรือเตรียมโมเดล

### 6.2 ส่วนประกอบหลัก

| ส่วน | ใช้ทำอะไร |
| --- | --- |
| Readiness | ดูคะแนนความพร้อมสำหรับ Dashboard, Analytics, Policy และ ML |
| Fields | ตรวจ completeness, validity, issue rate, quality score และสถานะรายฟิลด์ |
| Groups | เปรียบเทียบคุณภาพข้อมูลตาม cohort, province, country หรือ field group |
| Collection | ดูตัวแปรที่ควรเก็บเพิ่มและ issue ที่ต้องแก้จากต้นทาง |

### 6.3 วิธีใช้งาน

1. เปิดหน้า Data Quality
2. อ่าน warning ด้านบนเพื่อเข้าใจข้อจำกัดของข้อมูล
3. ดู scorecard ว่าข้อมูลพร้อมสำหรับ use case ใดมากน้อยแค่ไหน
4. ใช้ตัวกรองสถานะในแท็บ Fields เพื่อแยกฟิลด์ที่พร้อม ใช้ได้บางส่วน หรือมีปัญหา
5. เปิดแท็บ Groups เพื่อดูว่ากลุ่มใดมีคุณภาพข้อมูลต่ำกว่ากลุ่มอื่น
6. เปิดแท็บ Collection เพื่อดูรายการข้อมูลที่ควรเก็บเพิ่มในรอบถัดไป
7. เปิด expander นิยาม Data Readiness เพื่ออ่านความหมายของคะแนน

### 6.4 การแปลผล

- Completeness Score สูง หมายถึงข้อมูลไม่ค่อยขาด
- Validity Score สูง หมายถึงข้อมูลผ่านกฎรูปแบบและช่วงค่าที่กำหนด
- Issue Rate สูง หมายถึงมีปัญหาที่ควรแก้ไขหรือยืนยันโดย data owner
- ML readiness ไม่ใช่คุณภาพโมเดล แต่เป็นความพร้อมของข้อมูลสำหรับเริ่มออกแบบโมเดล

### 6.5 ข้อควรระวัง

- ฟิลด์ที่มี leakage risk ไม่ควรใช้เป็น feature เพื่อพยากรณ์ target ที่เกี่ยวข้อง
- Data Quality ใช้วัดความพร้อมของข้อมูล ไม่ได้พิสูจน์ causal impact ของโครงการ
- หากมี warning สำคัญ ควรให้ data owner ลงนามรับรองหรือแก้ไขก่อนใช้ในการตัดสินใจเชิงนโยบาย

## 7. คู่มือระบบ Analytics

### 7.1 วัตถุประสงค์

Analytics ใช้วิเคราะห์ผลลัพธ์เชิงลึก เปรียบเทียบ KPI ตามมิติที่เลือก และสร้าง visualization สำหรับตอบคำถามเชิงนโยบาย

### 7.2 ตัวกรอง

ใช้ตัวกรองชุดเดียวกับ Overview ได้แก่ ปีวิเคราะห์ รุ่น ประเทศ กลุ่มสาขา จังหวัด อำเภอ ภูมิภาค สาขารายละเอียด มหาวิทยาลัยมาตรฐาน และภาคส่วนผู้จ้าง

### 7.3 โหมดการวิเคราะห์

| โหมด | เหมาะกับใคร | ใช้ทำอะไร |
| --- | --- | --- |
| Executive View | ผู้บริหาร/ผู้กำหนดนโยบาย | ดู KPI ภาพรวม เกณฑ์อ้างอิง funnel และช่องว่างสำคัญ |
| Guided Visualization | ผู้ใช้ทั่วไป/นักนโยบาย | เลือกคำถามก่อน แล้วระบบแนะนำ visualization |
| Custom Visualization | นักวิเคราะห์ | เลือก chart, KPI และ dimension เอง |
| Data Quality View | Data steward/analyst | ตรวจ readiness และ missingness สำหรับการทำภาพ |

### 7.4 คำถามที่ Guided Visualization รองรับ

- จัดอันดับจำนวนผู้รับทุนตามมิติ
- ดูสัดส่วนหมวดหมู่ภายในมิติ
- ดูแนวโน้ม KPI
- ดูการกระจายรายได้
- ดูความสัมพันธ์ของผลลัพธ์
- ดูเส้นทางจากมิติหนึ่งไปยังผลลัพธ์ปลายทาง
- ตรวจความครบถ้วนข้อมูลติดตาม
- เปรียบเทียบช่องว่าง Completion และ Employment

### 7.5 Chart ที่พบในระบบ

- Dot Plot
- Treemap
- 100% Stacked Bar
- Donut
- Line
- Bubble
- Aggregate Box Plot
- Aggregate Histogram
- Heatmap
- Sankey
- Funnel
- Dumbbell

ระบบอาจเปลี่ยน chart ที่เลือกโดยอัตโนมัติหากไม่เหมาะสม เช่น เปลี่ยน Donut เป็น 100% Stacked Bar เมื่อมีหมวดหมู่มากเกินไป

### 7.6 Export

1. เลือกตัวกรองและโหมดวิเคราะห์
2. เลือก Role เป็น Analyst หรือ Admin
3. กด Export Aggregate CSV
4. ตรวจไฟล์ CSV ที่ได้ว่าเป็นข้อมูล aggregate ตาม filter ปัจจุบัน

### 7.7 ข้อควรระวัง

- ทุก visualization เป็น aggregate-only
- Box plot และ histogram ใช้สถิติรวม ไม่แสดงข้อมูลบุคคล
- สัดส่วนบางรายการคำนวณ denominator ก่อนปกปิดกลุ่มเล็ก เพื่อไม่ให้สัดส่วนของกลุ่มที่เหลือถูกตีความเกินจริง
- ผลลัพธ์ใช้เพื่อสนับสนุนการอภิปราย ไม่ใช่ข้อสรุปเชิงเหตุและผลโดยตรง

## 8. คู่มือระบบ Risk Forecast

### 8.1 วัตถุประสงค์

Risk Forecast ใช้ประเมินความเสี่ยงและแนวโน้มผลลัพธ์ของผู้รับทุนในระดับ aggregate และรายกรณีแบบมี human review

### 8.2 แท็บหลัก

| แท็บ | ใช้ทำอะไร |
| --- | --- |
| Overview | ดูคะแนนความเสี่ยงจากกฎและสถานการณ์รวม |
| Forecast | เลือกคำถามพยากรณ์ เลือกโมเดล และอ่านผลประเมิน |
| Individual | ประเมินแนวโน้มรายกรณีจาก CSV template ภายใต้สิทธิ์ที่กำหนด |
| Governance | ตรวจ readiness, label approval, agent responsibility และข้อจำกัด |

### 8.3 การใช้ Risk Overview

1. เปิดหน้า Risk Forecast
2. ใช้ตัวกรอง cohort, province และ field group ตามต้องการ
3. ดูสถานการณ์จากกฎประเมินความเสี่ยง
4. ตรวจปัจจัยที่ทำให้เกิดคะแนน เช่น component score และ triggered component
5. เปิด expander เพื่อดูตารางผลประเมินและผล graduation success แบบรวม

การอ่านผล risk score

- Low: ความเสี่ยงต่ำตามกฎ Prototype
- Medium: มีบางปัจจัยที่ต้องติดตาม
- High: เข้าเกณฑ์หลายปัจจัยหรือมีน้ำหนักความเสี่ยงสูง

ทุกระดับเป็นผลจากกฎต้นแบบใน `config/risk_rules.yaml` และต้องให้ผู้เชี่ยวชาญทบทวนก่อนใช้จริง

### 8.4 การใช้ Forecast

1. เลือกคำถามที่ต้องการพยากรณ์
2. อ่าน caveat หรือคำเตือนของ target
3. เลือกวิธีประเมินหรือโมเดลอย่างน้อย 1 รายการ
4. กดปุ่มรันโมเดล
5. อ่านผลลัพธ์ เช่น metric, confusion matrix, feature ที่ใช้ และข้อจำกัด
6. เปิดส่วนแปลผลเพื่อวางแผนนโยบาย

คำแนะนำ: ผู้ใช้ทั่วไปควรเริ่มจาก Key Forecast Objective มากกว่าเลือก target column เอง เพราะ target column ต้องเข้าใจนิยาม label และ leakage risk

### 8.5 การใช้ Individual Prediction

ระบบรายกรณีถูกออกแบบให้มีการทบทวนโดยมนุษย์ ไม่ใช่การอนุมัติอัตโนมัติ

ขั้นตอนสำหรับ CaseOfficer

1. เลือก Role เป็น `CaseOfficer`
2. เลือก target รายกรณี
3. ดาวน์โหลด template หรือดูตัวอย่างฟิลด์ที่ต้องใช้
4. อัปโหลด CSV ตาม template
5. ตรวจ warning เกี่ยวกับข้อมูล
6. ส่งผลเบื้องต้นให้ผู้ทบทวน

ขั้นตอนสำหรับ HumanReviewer

1. เลือก Role เป็น `HumanReviewer`
2. เปิดรายการที่รอตรวจสอบ
3. เลือก case id
4. ตรวจ features, data warnings และผลโมเดล
5. เลือก decision เช่น ยืนยัน ขอข้อมูลเพิ่ม หรือ override ตามเหตุผล

ขั้นตอนสำหรับ DomainApprover

1. เลือก Role เป็น `DomainApprover`
2. เปิดรายการที่รออนุมัติแผนช่วยเหลือ
3. ตรวจผล review และข้อเสนอแผน
4. เลือกอนุมัติหรือไม่อนุมัติ พร้อมเหตุผลประกอบ

ขั้นตอนสำหรับ DPOAuditor หรือ ModelOwner

1. เลือก role ที่เกี่ยวข้อง
2. ตรวจประวัติ audit และการใช้สิทธิ์
3. ตรวจ Model registry, threshold, calibration และข้อจำกัด

### 8.6 ข้อควรระวัง

- ผลรายกรณีไม่ใช่คำสั่งอนุมัติ ปฏิเสธ หรือจัดสรรทุน
- ห้ามใส่ข้อมูลระบุตัวบุคคลโดยตรงลงในไฟล์ที่ใช้ทดลอง หากไม่มีขั้นตอนกำกับดูแลที่ผ่านอนุมัติ
- ML บาง target อาจยังไม่เปิดใช้หาก label, train/test design หรือ leakage control ยังไม่พร้อม
- ต้องเก็บเหตุผลของการ override และการอนุมัติทุกครั้งเพื่อ audit trail

## 9. คู่มือระบบ Policy Recommendation

### 9.1 วัตถุประสงค์

Policy Recommendation ใช้จัดอันดับข้อเสนอเชิงนโยบายจากสูตร น้ำหนัก และหลักฐานข้อมูล ไม่ได้สร้างข้อเสนอจากข้อความ AI แบบไม่มีที่มา

### 9.2 ส่วนประกอบหลัก

| ส่วน | ใช้ทำอะไร |
| --- | --- |
| ตัวกรอง | เลือก cohort และ province |
| น้ำหนัก Field Recommendation | ปรับน้ำหนักคะแนนสำหรับการจัดอันดับกลุ่มสาขา |
| น้ำหนัก Area Allocation | ปรับน้ำหนักคะแนนสำหรับการจัดอันดับพื้นที่ |
| Field Recommendation Ranking | ดูผลคะแนนและอันดับกลุ่มสาขา |
| Area-based Allocation Ranking | ดูผลคะแนนและอันดับพื้นที่ |
| หลักฐาน สูตร น้ำหนัก และข้อจำกัด | ตรวจที่มาของคะแนนและข้อจำกัด |

### 9.3 วิธีใช้งาน

1. เปิดหน้า Policy Recommendation
2. เลือก cohort หรือ province หากต้องการวิเคราะห์เฉพาะกลุ่ม
3. ปรับน้ำหนัก Field Recommendation หรือ Area Allocation ตามโจทย์นโยบาย
4. อ่าน ranking table ที่แสดงคะแนน หลักฐาน และจำนวนข้อมูล
5. อ่านข้อเสนอเชิงนโยบายที่ระบบสรุปจาก ranking
6. เปิด expander เพื่อดูสูตร น้ำหนัก evidence columns และ limitations

### 9.4 การแปลผล

- คะแนนสูงหมายถึงกลุ่มหรือพื้นที่นั้นเข้าเงื่อนไขตามสูตรและน้ำหนักที่กำหนดมากกว่า
- หาก external indicators ยังไม่ผ่านการตรวจ ระบบจะไม่นำค่านั้นมาคำนวณ และจะแจ้ง warning
- การเปลี่ยนน้ำหนักจะคำนวณคะแนนใหม่ทันที

### 9.5 ข้อควรระวัง

- Ranking เป็น analysis result ไม่ใช่คำสั่งจัดสรรทุน
- สูตรและน้ำหนักใน Prototype ต้องให้ policy owner ตรวจสอบและลงนามก่อนใช้จริง
- ไม่ควรเปรียบเทียบพื้นที่หรือสาขาที่มีจำนวนข้อมูลต่ำกว่าเกณฑ์ขั้นต่ำ

## 10. คู่มือระบบ External Indicators

### 10.1 วัตถุประสงค์

External Indicators ใช้จัดการ template และตรวจ schema ของข้อมูลตัวชี้วัดภายนอกรายปี เช่น ความต้องการแรงงาน ค่าใช้จ่ายทุน ตัวชี้วัดความเหลื่อมล้ำ หรือ workforce demand

### 10.2 ฟิลด์ใน template

ไฟล์ template อยู่ที่ `data/reference/annual_external_indicators_template.csv`

| Field | ความหมาย |
| --- | --- |
| `indicator_year` | ปีของตัวชี้วัด |
| `indicator_type` | ประเภทตัวชี้วัด |
| `indicator_name` | ชื่อตัวชี้วัด |
| `geography_level` | ระดับพื้นที่ เช่น province หรือ district |
| `geography_code` | รหัสพื้นที่ |
| `field_code` | รหัสสาขา หากเกี่ยวข้อง |
| `value` | ค่าตัวชี้วัด |
| `unit` | หน่วย |
| `source` | แหล่งข้อมูล |
| `source_date` | วันที่ของแหล่งข้อมูล |
| `update_date` | วันที่อัปเดต |
| `reliability_level` | ระดับความน่าเชื่อถือ |
| `note` | หมายเหตุ |

### 10.3 วิธีดู template และ field definition

1. เปิดหน้า External Indicators
2. เลือก Role Mockup
3. อ่าน Prototype notice
4. ดูตาราง Template ข้อมูลเสริมรายปี
5. ดู Field Definition เพื่อเข้าใจความหมายและรูปแบบข้อมูล
6. ดู Aggregate Summary เพื่อประเมินข้อมูลที่มีอยู่

### 10.4 วิธี import mockup

เฉพาะ Admin เท่านั้นที่เห็นเมนูนำเข้า

1. เลือก Role เป็น `Admin`
2. เตรียม CSV ให้มีคอลัมน์ตาม template
3. กด upload ในส่วน Import Mockup
4. ระบบตรวจ schema ใน session ปัจจุบัน
5. หากผ่าน ระบบจะแจ้งว่าไฟล์ผ่านการตรวจ schema แล้ว

### 10.5 การดาวน์โหลด template

กดปุ่ม download บนหน้า External Indicators เพื่อรับไฟล์ template สำหรับกรอกข้อมูลรอบถัดไป

### 10.6 ข้อควรระวัง

- Import mockup ยังไม่ใช่ staging/approval workflow สำหรับ production
- ต้องมีเจ้าของข้อมูล แหล่งข้อมูล วันที่อัปเดต และ reliability level ที่ชัดเจน
- ตัวชี้วัดภายนอกควรผ่าน governance review ก่อนนำไปคำนวณ policy ranking

## 11. คู่มือระบบ Governance

### 11.1 วัตถุประสงค์

Governance ใช้ตรวจสิทธิ์ บทบาท นโยบายการใช้ข้อมูล การปกปิดกลุ่มเล็ก การ mask ข้อมูลที่คล้าย PII และ audit/export log

### 11.2 ส่วนประกอบหลัก

| ส่วน | ใช้ทำอะไร |
| --- | --- |
| Role Matrix | ดูสิทธิ์ของแต่ละ role |
| Data Use Notice | อ่านข้อกำหนดการใช้ข้อมูล |
| ข้อมูลที่ห้ามแสดงหรือ Export | รายการ forbidden columns |
| Minimum Group Size Masking | ตรวจการปกปิดกลุ่มขนาดเล็ก |
| PII Masking Demo | ดูตัวอย่างการ mask phone/email/เลข 13 หลัก |
| Audit Log | ดูเหตุการณ์ audit ตามสิทธิ์ |
| Export Log | ดูประวัติการ export ตามสิทธิ์ |
| Privacy Self Check | ตรวจหลักการ privacy ของ Prototype |

### 11.3 วิธีใช้งาน

1. เปิดหน้า Governance
2. เลือก Role Mockup
3. อ่าน Prototype notice และ Data Use Notice
4. ดู Role Matrix เพื่อเข้าใจสิทธิ์แต่ละ role
5. ตรวจ forbidden columns ว่าข้อมูลประเภทใดห้ามแสดงหรือส่งออก
6. ดู Minimum Group Size Masking เพื่อยืนยันว่ากลุ่มเล็กถูกปกปิด
7. ดู PII Masking Demo เพื่อเข้าใจการ mask ข้อมูลรูปแบบเสี่ยง
8. หาก role มีสิทธิ์ ให้เปิด Audit Log และ Export Log
9. ใช้ Privacy Self Check ก่อนนำผลไปสาธิตหรือส่งต่อ

### 11.4 นโยบายสำคัญ

- ใช้ข้อมูลเพื่อสาธิตระบบสนับสนุนนโยบายเท่านั้น
- ห้ามใช้ผลลัพธ์ Prototype เพื่อตัดสินใจจัดสรรทุนอัตโนมัติ
- ห้ามส่งออกหรือเปิดเผยข้อมูลระดับบุคคล
- กลุ่มข้อมูลที่มีจำนวนน้อยกว่า minimum group size ต้องถูกปกปิด
- Export ต้องเป็น aggregate-only และควรมี log

## 12. คู่มือระบบ Help Documentation

### 12.1 วัตถุประสงค์

Help Documentation ใช้ค้นหาเอกสารภายในระบบ อ่านคู่มือ ถามตอบจากเอกสาร และดู FAQ/Privacy guidance

### 12.2 การค้นหาเอกสาร

1. เปิดหน้า Help Documentation
2. พิมพ์คำค้นในช่องค้นหา เช่น `privacy`, `target`, `CSV`, `forecast`
3. เปิดผลลัพธ์เพื่ออ่านข้อความสรุปและชื่อเอกสารต้นทาง

### 12.3 Quick Links

| Quick Link | ใช้ทำอะไร |
| --- | --- |
| Documentation | อ่านเอกสารในโฟลเดอร์ `docs/` |
| AI-assisted integration | ถาม Local AI จากเอกสารภายในเครื่อง |
| FAQ | อ่านคำถามที่พบบ่อย |
| Privacy & Governance | อ่านข้อห้ามและแนวปฏิบัติด้านข้อมูล |

### 12.4 การใช้ Local AI

ระบบรองรับ Ollama ที่รันบนเครื่องผู้ใช้

ขั้นตอน

1. ติดตั้ง Ollama หากยังไม่มี
2. ดาวน์โหลดโมเดล เช่น `ollama pull qwen2.5:3b`
3. เปิด Ollama
4. ในหน้า Help Documentation เลือก AI-assisted integration
5. ใช้ endpoint `http://localhost:11434`
6. กดตรวจสอบ
7. เลือกโมเดลและถามคำถามเกี่ยวกับเอกสารหรือขั้นตอนใช้งาน

ข้อควรระวัง

- ห้ามวางชื่อ เลขบัตร อีเมล เบอร์โทรศัพท์ หรือข้อมูลระบุตัวบุคคลลงในช่องถาม AI
- หน้า Help ส่งเฉพาะคำถามและข้อความจากเอกสาร ไม่ควรส่งฐานข้อมูลผู้รับทุนให้ AI
- endpoint ถูกออกแบบให้ใช้ localhost เพื่อความปลอดภัยของ Prototype

## 13. คู่มือ Data Pipeline และผู้ดูแลระบบ

### 13.1 วัตถุประสงค์

Data Pipeline ใช้แปลง raw Excel ภายนอก repo ให้เป็น cleaned no-PII dataset, validation issues, quality report และ processing log

### 13.2 ขั้นตอน pipeline

1. อ่าน Excel workbook
2. ตรวจ sheet ที่จำเป็น เช่น `DB_Students` และ `Remark`
3. ตรวจ required columns
4. อ่านแถวที่มี source `ID`
5. ทำความสะอาดและ standardize no-PII fields
6. แปลง spreadsheet errors เช่น `#NUM!` เป็น missing values
7. parse วันที่และรายได้
8. คำนวณ study duration
9. validate duplicate IDs, date order, income range, dictionary values และ key-field completeness
10. ตรวจ cross-field relationships
11. classify field ตาม datatype, readiness, aggregate-only policy, ML role และ leakage risk
12. เขียนผลลัพธ์ออกไปยัง `data/processed/phase4/`

### 13.3 คำสั่งรัน pipeline

```powershell
python scripts/run_phase4_pipeline.py
```

หรือใช้ launcher

```text
launchers/04_phase4_data_pipeline.bat
```

### 13.4 Output สำคัญ

| Output | ใช้ทำอะไร |
| --- | --- |
| `cleaned_modeling_dataset_no_pii.csv` | ชุดข้อมูลสะอาดสำหรับ dashboard/analytics |
| `validation_issues.csv` | รายการปัญหาที่พบ |
| `field_cleaning_report.csv` | รายงานคุณภาพและ readiness รายฟิลด์ |
| `processing_log.jsonl` | log การประมวลผล |
| `before_after_report.md` | สรุปก่อน/หลังทำความสะอาดข้อมูล |
| `latest_import_manifest.json` | manifest การ import ล่าสุด |

### 13.5 กฎสำหรับผู้ดูแลข้อมูล

- ห้ามแก้ไข raw data โดยตรงผ่าน pipeline
- ห้าม commit raw Excel หรือข้อมูลที่มี PII
- failed/invalid records ไม่ถูกลบทิ้ง แต่ถูกบันทึกเป็น issues
- หาก source hash เปลี่ยน ต้องตรวจ processing log และรายงานคุณภาพใหม่

## 14. คู่มือ Acceptance และ Handover

ก่อนส่งมอบหรือสาธิตระบบอย่างเป็นทางการ ให้รัน acceptance suite

```powershell
python scripts/phase8_acceptance.py
```

สถานการณ์ทดสอบที่ควรทำด้วยมือ

1. เปิดแอปด้วย `streamlit run app.py`
2. เปิด Overview และจด total recipients, completion count, employment count, country count และ field-group count
3. เลือก cohort และ province อย่างละหนึ่งรายการ แล้วตรวจว่า KPI และ chart เปลี่ยนตาม filter
4. เปิด Data Quality และตรวจ missing fields, validation issues, dashboard readiness และ model readiness
5. เปิด Analytics และเปรียบเทียบ completion, employment, income, field-job fit และ local fit
6. เปิด Risk Forecast และตรวจ score, risk level, triggered components, timestamp, rule version และ limitations
7. เปิด Policy Recommendation ปรับ weight และตรวจว่า ranking recalculates
8. เปิด External Indicators เป็น Admin แล้วตรวจ template/schema check จากนั้นสลับเป็น Viewer เพื่อยืนยันว่า import ไม่แสดง
9. เปิด Governance และตรวจ prototype notice, minimum group-size masking, audit/export visibility และ aggregate-only export

## 15. ข้อจำกัดของ Prototype

- เป็น local Streamlit และ SQLite Prototype ไม่ใช่ระบบ multi-user production
- Role selection เป็น mockup ไม่ใช่ authentication จริง
- External indicators เป็น template/sample ต้องมีแหล่งข้อมูลรายปีที่ตรวจสอบแล้วก่อนใช้จริง
- Risk scores เป็น rule-based prototype ต้องผ่าน expert approval
- Graduation forecasting และ ML workflow ต้องมี label approval, leakage review, calibration และ monitoring ก่อน operational use
- Upload validation เป็น schema check เบื้องต้น ยังไม่มี staging, approval, rollback หรือ asynchronous processing
- Export เป็น aggregate-only แต่ production ยังต้องมี server-side authorization, encryption, retention และ incident response

## 16. แนวทางแก้ปัญหาเบื้องต้น

| อาการ | วิธีตรวจ/แก้ไข |
| --- | --- |
| เปิดแอปไม่ได้ | ตรวจว่าอยู่ในโฟลเดอร์ `odos-policy-analytics`, activate `.venv`, และติดตั้ง `requirements.txt` แล้ว |
| ไม่พบคำสั่ง streamlit | รัน `python -m pip install -r requirements.txt` |
| หน้า dashboard ไม่มีข้อมูล | รัน `python scripts/import_data.py` และ `python scripts/build_database.py` หรือรัน Phase 4 pipeline |
| ตัวกรองแล้วข้อมูลหาย | ลดจำนวนตัวกรอง หรือเลือกค่าที่มีข้อมูลจริง |
| export ไม่ได้ | ตรวจ role ว่าเป็น Analyst หรือ Admin |
| Viewer ไม่เห็น import/log | เป็นพฤติกรรมที่ถูกต้องตาม role mockup |
| external indicator upload ไม่ผ่าน | ตรวจชื่อคอลัมน์และชนิดข้อมูลให้ตรงกับ template |
| ผล Risk/Policy ดูขัดกับบริบทจริง | ตรวจ rule/weight ใน config และส่งให้ผู้เชี่ยวชาญ review ก่อนใช้ |
| Local AI ใช้ไม่ได้ | ตรวจว่า Ollama เปิดอยู่ endpoint เป็น `http://localhost:11434` และมีโมเดลติดตั้งแล้ว |

## 17. คำศัพท์สำคัญ

| คำ | ความหมาย |
| --- | --- |
| Aggregate | ข้อมูลสรุปรวม ไม่ใช่ข้อมูลรายบุคคล |
| Minimum Group Size | จำนวนขั้นต่ำของกลุ่มก่อนจะแสดงผล เพื่อลดความเสี่ยงระบุตัวบุคคล |
| PII | ข้อมูลที่ระบุตัวบุคคลได้ เช่น ชื่อ เลขบัตร อีเมล เบอร์โทรศัพท์ |
| Data Leakage | การใช้ข้อมูลที่ไม่ควรรู้ ณ เวลาพยากรณ์หรือเกี่ยวข้องกับ target มากเกินไป |
| Readiness | ความพร้อมของข้อมูลสำหรับ use case เช่น dashboard, analytics, policy หรือ ML |
| Rule-based Risk | การประเมินความเสี่ยงจากกฎและน้ำหนักที่กำหนดไว้ |
| Human Review | ขั้นตอนให้มนุษย์ตรวจผลก่อนนำไปใช้ |
| Audit Log | บันทึกเหตุการณ์เพื่อการตรวจสอบย้อนหลัง |
| Export Log | บันทึกการส่งออกข้อมูล |

## 18. เอกสารอ้างอิงภายใน repository

- `README.md`
- `docs/architecture.md`
- `docs/dashboard_analytics.md`
- `docs/data_pipeline_quality.md`
- `docs/risk_forecast_policy.md`
- `docs/external_indicators_governance.md`
- `docs/phase8_handover.md`
- `docs/deployment.md`
- `config/metrics.yaml`
- `config/risk_rules.yaml`
- `config/policy_recommendation.yaml`
- `config/governance.yaml`
- `config/visualization.yaml`

