# Sequence Diagram: ระบบขาย RAM หน้าร้านและตัดสต็อก (US-02)

ไดอะแกรมแสดงขั้นตอนการทำงานเมื่อพนักงานสแกน Serial Number เพื่อขายสินค้าหน้าร้าน ตรวจสอบความถูกต้อง ตัดสต็อก และตรวจสอบการแจ้งเตือนสต็อกต่ำ

```mermaid
sequenceDiagram
    autonumber
    actor Staff as พนักงาน (Staff)
    participant UI as ระบบ POS / CLI (main.py)
    participant Sale as Sale
    participant Serial as SerialNumber
    participant Inv as Inventory
    participant DB as items.json

    Staff->>UI: สแกน/กรอก Serial Number
    Staff->>UI: กดยืนยันการขาย (confirmSale)
    UI->>Sale: confirmSale(serialNo)
    Sale->>Serial: scan(serialNo)
    Serial->>DB: ค้นหาข้อมูล Serial Number

    alt ไม่พบ Serial Number ในระบบ
        DB-->>Serial: Not Found
        Serial-->>Sale: ข้อผิดพลาด "ไม่พบสินค้า"
        Sale-->>UI: แสดงผลลัพธ์ไม่สำเร็จ
        UI-->>Staff: แสดงข้อความแจ้งเตือน "ไม่พบสินค้า"

    else Serial Number มีสถานะเป็น SOLD อยู่แล้ว (ป้องกันขายซ้ำ)
        DB-->>Serial: status == SOLD
        Serial-->>Sale: ข้อผิดพลาด "Serial Number ดังกล่าวไม่สามารถขายซ้ำได้"
        Sale-->>UI: แสดงผลลัพธ์ไม่สำเร็จ
        UI-->>Staff: แจ้งเตือน "Serial Number ดังกล่าวไม่สามารถขายซ้ำได้"

    else Serial Number พร้อมขาย (status == IN_STOCK)
        DB-->>Serial: status == IN_STOCK
        Serial->>DB: อัปเดต status = SOLD
        
        Sale->>Inv: deductStock(quantity = 1)
        Inv->>DB: ลด stockQty ลง 1 ชิ้น
        
        Inv->>Inv: checkLowStockAlert()
        alt stockQty < lowStockThreshold
            Inv-->>Sale: แจ้งเตือน: "สต็อกต่ำกว่าเกณฑ์"
        else stockQty >= lowStockThreshold
            Inv-->>Sale: ไม่มีข้อความแจ้งเตือนสต็อกต่ำ
        end

        Sale->>DB: บันทึกรายการลงไฟล์ (save_data)
        Sale-->>UI: ยืนยันการขายสำเร็จ (แจ้งยอดคงเหลือล่าสุด)
        UI-->>Staff: แสดงผลการขายสำเร็จ
        opt มีแจ้งเตือนสต็อกต่ำ
            UI-->>Staff: แสดงข้อความเตือน "สต็อกต่ำกว่าเกณฑ์ (คงเหลือ N ชิ้น)"
        end
    end
