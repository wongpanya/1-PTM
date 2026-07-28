# ODOS Prototype Agent Team

Agent ในโฟลเดอร์นี้เป็นบทบาทช่วยงานแบบ Human-in-the-loop ไม่ใช่ผู้อนุมัติอัตโนมัติ แต่ละ Agent ต้องอ่าน `AGENTS.md`, `config/agents.yaml`, `config/labeling.yaml` และกฎของโมดูลที่เกี่ยวข้องก่อนทำงาน

## Operating Rules

1. ใช้ข้อมูล no-PII และแสดงผล aggregate เป็นค่าเริ่มต้น
2. Agent เสนอ Label หรือกฎได้ แต่ห้ามรับรองผลงานของตนเอง
3. Label ที่มีสถานะอื่นนอกจาก `approved` ห้ามใช้เป็น Production ML target
4. ทุกผลลัพธ์ต้องระบุ source snapshot, rule/label version, evidence และข้อจำกัด
5. เมื่อหลักฐานไม่พอ ให้ใช้ `abstain` หรือ `needs_review` ห้ามเดาค่า

## Role Cards

- `data_steward.md`
- `analytics.md`
- `risk.md`
- `policy.md`
- `external_indicator.md`
- `governance.md`
- `technical.md`
