# Phase 0 Acceptance Checklist

เอกสารนี้ใช้ตรวจรับ Phase 0: ล็อกขอบเขต Prototype

## Scope Documents

- [x] มี `PROJECT_SCOPE.md`
- [x] มี `docs/phase0/PROJECT_CHARTER.md`
- [x] มี `docs/phase0/ACCEPTANCE_CHECKLIST.md`
- [x] มี `docs/phase0/DECISION_LOG.md`

## Prototype Boundary

- [x] ระบุชัดว่าเป็น Prototype ไม่ใช่ Production System
- [x] ระบุชัดว่าเป็นระบบสนับสนุนการวิเคราะห์เชิงนโยบาย
- [x] ระบุชัดว่าไม่ใช่ระบบตัดสินใจจัดสรรทุนอัตโนมัติ
- [x] ระบุขอบเขต in-scope
- [x] ระบุขอบเขต out-of-scope

## Required Pages

- [x] Overview
- [x] Data Quality
- [x] Analytics
- [x] Risk & Forecast
- [x] Policy Recommendation
- [x] External Indicators
- [x] Governance

## Data Decisions

- [x] ระบุ source data สำหรับ Prototype
- [x] ระบุว่าจะใช้ฐานข้อมูลกลาง/cleaned CSV เป็น runtime data source
- [x] ระบุว่า Excel ต้นฉบับไม่ควรถูกอ่านทุกครั้งใน runtime app
- [x] ระบุ upload policy สำหรับรอบแรก
- [x] ระบุรายการข้อมูลที่ห้ามแสดงหรือ export
- [x] ระบุแนวทางใช้ข้อมูลจริงแบบลดการระบุตัวตน

## User and Language Decisions

- [x] ระบุผู้ใช้หลัก
- [x] ระบุภาษาใช้งานของระบบรอบแรก
- [x] ระบุว่าคำอังกฤษใช้ได้เมื่อเป็นคำเทคนิคหรือชื่อโมดูล

## Technology Decisions

- [x] ระบุ technology baseline
- [x] ระบุแนวทางใช้เครื่องมือฟรีหรือ free tier ก่อน
- [x] ระบุ deployment direction

## Governance Decisions

- [x] ระบุ PII masking concept
- [x] ระบุ role concept
- [x] ระบุ audit log concept
- [x] ระบุ export policy concept
- [x] ระบุว่า PDPA workflow เต็มรูปแบบอยู่นอกขอบเขต Prototype

## Prototype Acceptance Criteria

- [x] มี acceptance criteria สำหรับ Prototype Phase 0-8
- [x] มี Phase 0 completion criteria
- [x] มี roadmap ไป Phase 2

## Phase 0 Result

Phase 0 status: Passed

ขอบเขต Prototype ถูกล็อกเพียงพอสำหรับเริ่ม Phase 2: เตรียม Repository ให้ Codex
