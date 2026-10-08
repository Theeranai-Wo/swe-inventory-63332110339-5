# AI Rules & Constraints

## ขอบเขตและข้อห้าม (Out of Scope Enforcement)
1. **ห้ามใช้ Network / External Services จริง:**
   - ห้าม import หรือใช้งาน `smtplib`, `socket`, `requests` หรือบริการส่งอีเมล/SMS จริงโดยเด็ดขาด
   - การแจ้งเตือนสต็อกต่ำ (Low Stock Alert) และการแจ้งเตือนแชท ให้จำลองผ่าน console ด้วย `print()` หรือ return ข้อความในระดับ service เท่านั้น
2. **ห้ามใช้ Database ภายนอก:**
   - ใช้เฉพาะไฟล์ `items.json` ในการอ่านและบันทึกข้อมูล
3. **Data Integrity & Business Logic:**
   - การตัดสต็อกสินค้าต้องทำผ่านการสแกน Serial Number ที่ถูกต้องและมีสถานะ `IN_STOCK` เท่านั้น
   - เมื่อตัดสต็อกสำเร็จ ต้องเปลี่ยนสถานะเป็น `SOLD` และลด `stockQuantity` ของสินค้า 1 ชิ้นทันที ห้ามเกิดยอดติดลบ
   - ห้ามขาย Serial Number ที่มีสถานะ `SOLD` ซ้ำเด็ดขาด
   - การคำนวณแจ้งเตือนสต็อกต่ำ: แจ้งเตือนเมื่อ `stockQuantity < lowStockThreshold` (ต่ำกว่าเกณฑ์เท่านั้น กรณีเท่ากับพอดีไม่ต้องแจ้งเตือน)
