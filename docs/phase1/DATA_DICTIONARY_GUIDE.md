# Phase 1 Data Dictionary Guide

Data Dictionary ของ Phase 1 อยู่ที่:

- `phase1_outputs/data/data_dictionary.csv`

ไฟล์นี้สร้างจากคอลัมน์ต้นฉบับทั้งหมด 112 คอลัมน์ในชีต `DB_Students`

## Columns in Data Dictionary

| Column | Meaning |
| --- | --- |
| `original_col_no` | ลำดับคอลัมน์ในไฟล์ Excel ต้นฉบับ |
| `original_header` | ชื่อหัวคอลัมน์จากไฟล์ต้นฉบับ |
| `mapped_field` | ชื่อ field ที่ map เข้ากับ schema Prototype |
| `category` | หมวดข้อมูล เช่น student, education, employment |
| `include_in_prototype` | สถานะการใช้ใน Prototype: yes, no, review |
| `non_empty_count` | จำนวน record ที่มีค่า |
| `missing_count` | จำนวน record ที่ไม่มีค่า |
| `completeness_pct` | อัตราความครบถ้วนของข้อมูล |
| `error_like_count` | จำนวนค่าที่เป็น error-like เช่น `#NUM!` |
| `top_values_sample` | ตัวอย่างค่าที่พบบ่อย |

## Prototype Use

ใช้ Data Dictionary เพื่อ:

- เลือก field สำหรับ dashboard
- ระบุ field ที่พร้อมใช้กับ risk/forecast
- ระบุ field ที่ต้อง clean เพิ่ม
- แยก field ที่เสี่ยง PII หรือ free text
- ตรวจสอบความครบถ้วนก่อนนำข้อมูลไปวิเคราะห์

## Current Classification

Phase 1 แบ่งคอลัมน์เป็น 3 สถานะ

- `yes`: ใช้ใน Prototype ได้
- `no`: ไม่ใช้ใน Prototype เพราะเป็น PII, sensitive, contact, detailed address หรือไม่จำเป็นต่อรอบแรก
- `review`: ยังไม่ได้ map เข้า schema หลัก หรือควรให้ domain owner ตรวจนิยามก่อนใช้

## Recommended Review by Data Owner

ผู้รับรองนิยามข้อมูลควรตรวจอย่างน้อย:

- สถานะโครงการและสถานะปัจจุบัน
- ประเทศและกลุ่มสาขาวิชา
- ประเภทการประกอบอาชีพ
- ความสอดคล้องงานกับสาขา
- ความสอดคล้องงานกับท้องถิ่น
- นิยามรายได้
- ข้อมูลที่ห้ามแสดงหรือห้าม export

## Phase 1 Status

Data Dictionary status: Ready for Prototype, pending data owner sign-off
