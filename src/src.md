# Source Code Architecture & Implementation Guide (`src.md`)

เอกสารสรุปโครงสร้างซอร์สโค้ด โมดูล และความรับผิดชอบของคลาสในระบบจัดการสต็อกและค้นหา RAM

---

## 1. โครงสร้างโฟลเดอร์และไฟล์ (File Structure)

```text
├── src/
│   ├── inventory.py   # Business Logic, Domain Service และ Design Patterns (Factory + Observer)
│   └── main.py        # Presentation Layer / CLI Entry Point สำหรับผู้ใช้งาน
├── items.json         # Mock Database เก็บข้อมูลสินค้า RAM, Serial Numbers และ Chat Requests
└── src.md             # เอกสารอธิบายภาพรวมซอร์สโค้ด
