# Agents, Human Resources, and Labeling Plan

## Purpose

ทรัพยากรชุดนี้เตรียมระบบสำหรับทดลอง Explainable ML ในอนาคต โดยยังไม่เริ่มฝึกโมเดลจนกว่า Label หลักจะได้รับการรับรองและมีการแยกข้อมูลตามรุ่นหรือเวลา

## Hybrid Team

| Agent | ผู้รับผิดชอบมนุษย์ | งาน Label | Prototype effort |
| --- | --- | --- | ---: |
| Data Steward | Data owner/เจ้าหน้าที่ข้อมูล | ตรวจหลักฐาน mapping และข้อยกเว้น | 1.0 person-day |
| Analytics | นักวิเคราะห์ข้อมูล/นโยบาย | ตรวจ class balance, KPI และ cohort profile | 0.75 person-day |
| Risk | ผู้เชี่ยวชาญทุน/การศึกษา | รับรองนิยาม outcome, rule และ threshold | 0.75 person-day |
| Policy | Policy owner/คณะผู้เชี่ยวชาญ | รับรองวัตถุประสงค์และข้อจำกัดการใช้ผล | 0.50 person-day |
| External Indicator | Source owner/นักเศรษฐศาสตร์ | รับรอง feature ภายนอกและรอบปี | 0.50 person-day |
| Governance | DPO/กฎหมาย/ความมั่นคงปลอดภัย | Privacy, fairness, access และ retention gate | 0.50 person-day |
| Technical | Developer/DevOps | Pipeline, lineage, tests และ deployment | 2.00 person-days |

รวมประมาณ 6 person-days ทำแบบขนานได้ด้วยทีมขั้นต่ำ 4 คนภายใน 2-3 วันสำหรับ Prototype ผู้เชี่ยวชาญบางคนอาจรับหลายบทบาทได้ แต่ผู้เสนอ Label ไม่ควรเป็นผู้อนุมัติคนเดียวกัน

## Minimum Human Team

1. Data and Analytics Lead: รับบท Data Steward + Analytics
2. Scholarship Domain Lead: รับบท Risk + Policy
3. Governance Reviewer: รับบท Governance และประสานเจ้าของ external source
4. Technical Lead: รับบท Technical

Agent ลดภาระการเตรียมรายงาน ตรวจ schema สร้าง review queue และตรวจความสอดคล้อง แต่ไม่ทดแทน Data owner, domain expert, Policy owner หรือ DPO ในการลงนามรับรอง

## Label Priority

1. `target_graduation_success` เป็น Label แรกสำหรับทดลอง Logistic Regression หรือ Decision Tree
2. `target_dropout`, `target_termination`, `target_scholarship_risk`, `target_tracking_risk` ใช้ทดลอง risk monitoring หลังรับรองวันที่อ้างอิง
3. `target_employment_ready`, `target_field_mismatch`, `target_local_mismatch` ใช้เมื่อข้อมูลติดตามหลังทุนครบและนิยาม outcome ผ่านการรับรอง

## Label Workflow

1. Freeze source snapshot และบันทึก `source_snapshot_id`
2. Data Steward Agent เตรียม evidence และตรวจ missing/invalid values
3. Risk หรือ Analytics Agent เสนอ Label พร้อม `label_version`
4. ผู้ตรวจมนุษย์เลือก `approved`, `rejected`, `needs_review` หรือ `abstain`
5. กรณีสุ่มตรวจสองคน ต้องมี agreement อย่างน้อย 0.80; ข้อขัดแย้งส่งให้ Scholarship Domain Lead
6. Governance Agent ตรวจ PII, fairness, retention และสิทธิ์เข้าถึง
7. Technical Agent freeze label snapshot และแยก train/test ตาม cohort หรือเวลา
8. Label สถานะ `approved_for_prototype` หรือ `approved` และ readiness อย่างน้อย 85 จึงใช้ทดลอง ML; Production ใช้ได้เฉพาะ `approved`

## Prototype Approval Decision

วันที่ 2026-07-28 Project owner ยืนยัน Label ทั้ง 8 รายการตามข้อเสนอของ Agent สำหรับ `prototype_ml_experiment_only` จึงกำหนดสถานะเป็น `approved_for_prototype`

- อนุญาต: ทดลองโมเดลแบบอธิบายได้ ประเมิน feasibility และรายงานข้อจำกัด
- ไม่อนุญาต: ใช้ตัดสินใจจัดสรรทุน ใช้กับบุคคลจริง หรือ deploy เป็น Production model
- Production approval ยังคงต้องได้รับการรับรองจากผู้เชี่ยวชาญตาม `human_approver_role`
- หลักฐานการอนุมัติอยู่ที่ `data/reference/label_approval_register.csv`

## Leakage Controls

- Feature ทุกตัวต้องเกิดก่อน outcome cutoff ของแต่ละ Label
- ห้ามใช้ `target_*`, Risk score, outcome status หรือข้อมูลหลังเหตุการณ์เป็น feature
- แยก train/test ตาม cohort หรือเวลา ไม่สุ่มข้ามช่วงเวลาโดยไม่มีเหตุผล
- เก็บ Label ระดับบุคคลเฉพาะพื้นที่ภายในที่ควบคุมสิทธิ์ หน้าจอและ export ใช้ aggregate

## Artifacts

- Agent registry: `config/agents.yaml`
- Label policy: `config/labeling.yaml`
- Review template: `data/reference/label_review_template.csv`
- Validator: `python scripts/validate_labels.py`
- Runtime registry: `src/agents/registry.py`
- Label readiness: `src/labeling/workflow.py`
