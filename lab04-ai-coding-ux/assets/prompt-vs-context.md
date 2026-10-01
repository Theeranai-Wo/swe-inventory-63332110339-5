# การเปรียบเทียบ Prompt แบบสั้น กับ Prompt ที่มี Context

## รอบที่ 1: Prompt สั้นๆ
**Prompt ที่ใช้:**
ช่วยเขียนเมธอด sell_many(orders: dict[str, int]) สำหรับขายสินค้าหลายรายการพร้อมกันในคลังสินค้าให้หน่อย ใช้ภาษา Python

**ผลลัพธ์ที่ AI ให้มา:**
ได้ ถ้า orders เป็นรูปแบบ {ชื่อสินค้า: จำนวนที่ขาย} เมธอด sell_many() สามารถตรวจสอบสินค้าทุกรายการก่อน แล้วค่อยตัดสต๊อกทีเดียว เพื่อป้องกันกรณีขายบางรายการสำเร็จแต่บางรายการไม่สำเร็จ
def sell_many(self, orders: dict[str, int]):
    # ตรวจสอบรายการทั้งหมดก่อน
    for product, quantity in orders.items():
        if product not in self.stock:
            raise ValueError(f"ไม่พบสินค้า: {product}")

        if quantity <= 0:
            raise ValueError(f"จำนวนสินค้าต้องมากกว่า 0: {product}")

        if self.stock[product] < quantity:
            raise ValueError(
                f"สินค้า {product} มีไม่พอ "
                f"(เหลือ {self.stock[product]}, ต้องการ {quantity})"
            )

    # ถ้าทุกรายการผ่าน จึงค่อยตัดสต๊อก
    for product, quantity in orders.items():
        self.stock[product] -= quantity

    return True

ตัวอย่าง ถ้าคลังมี:
self.stock = {
    "RAM 16GB": 10,
    "SSD 1TB": 5,
    "CPU": 3
}

ขายพร้อมกัน:

orders = {
    "RAM 16GB": 2,
    "SSD 1TB": 1,
    "CPU": 1
}

inventory.sell_many(orders)

ผลลัพธ์:

{
    "RAM 16GB": 8,
    "SSD 1TB": 4,
    "CPU": 2
}

จุดสำคัญคือแยกเป็น 2 รอบ: รอบแรกตรวจสอบทุกสินค้า → รอบสองค่อยหักสต๊อก ดังนั้นถ้า SSD 1TB มีไม่พอ จะไม่มีรายการไหนถูกหักสต๊อกเลย.

---

## รอบที่ 2: Prompt ที่แนบ Context ครบถ้วน
**Prompt ที่ใช้:**
ปรับปรุงเมธอด sell() ของคลาส Inventory ด้านล่างให้รองรับการขายหลายรายการพร้อมกัน
from abc import ABC, abstractmethod
import json
import os

DATA_FILE = "items.json"

==========================================
Observer Pattern: Notifier Interface & Implementations
==========================================

class BaseNotifier(ABC):
@abstractmethod
def send(self, message: str) -> None:
pass

class ConsoleNotifier(BaseNotifier):
def send(self, message: str) -> None:
print(f"\n[ALERT - Console] {message}")

class LogNotifier(BaseNotifier):
def send(self, message: str) -> None:
print(f"\n[LOG FILE MOCK] Written to audit log: {message}")

==========================================
Factory Pattern: NotifierFactory
==========================================

class NotifierFactory:
@staticmethod
def create(channel: str) -> BaseNotifier:
channel_lower = channel.strip().lower()
if channel_lower == "console":
return ConsoleNotifier()
elif channel_lower == "log":
return LogNotifier()
else:
raise ValueError(f"Unknown notification channel: {channel}")

==========================================
Core Domain & InventoryService (DIP + Observer Subject)
==========================================

class InventoryService:
def init(self, observers: list[BaseNotifier] = None):
# รับ Observers ผ่าน Constructor (Dependency Inversion Principle)
self.observers: list[BaseNotifier] = observers if observers is not None else []

def attach(self, observer: BaseNotifier) -> None:
    if observer not in self.observers:
        self.observers.append(observer)

def detach(self, observer: BaseNotifier) -> None:
    if observer in self.observers:
        self.observers.remove(observer)

def notify_all(self, message: str) -> None:
    for observer in self.observers:
        observer.send(message)

def load_data(self) -> dict:
    if not os.path.exists(DATA_FILE):
        return {"products": [], "serials": [], "chat_requests": []}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(self, data: dict) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def filter_ram(self, require_rgb=False, sync_system=None, brand=None, package_type=None, min_capacity=None):
    data = self.load_data()
    results = data.get("products", [])
    if require_rgb:
        results = [p for p in results if p.get("hasRgb")]
    if sync_system:
        results = [p for p in results if sync_system in p.get("rgbSyncSystems", [])]
    if brand:
        results = [p for p in results if p.get("brand", "").lower() == brand.lower()]
    if package_type:
        results = [p for p in results if p.get("packageType", "").upper() == package_type.upper()]
    if min_capacity is not None:
        results = [p for p in results if p.get("capacity", 0) >= min_capacity]
    return results

def sell_by_serial(self, serial_number: str) -> tuple[bool, str, str | None]:
    data = self.load_data()
    serials = data.get("serials", [])
    products = data.get("products", [])

    target_serial = next((s for s in serials if s["serialNumber"] == serial_number), None)
    if not target_serial:
        return False, "ไม่พบสินค้า", None

    if target_serial.get("status") == "SOLD":
        return False, "Serial Number ดังกล่าวไม่สามารถขายซ้ำได้", None

    target_prod = next((p for p in products if p["productId"] == target_serial["productId"]), None)
    if not target_prod or target_prod.get("stockQuantity", 0) <= 0:
        return False, "จำนวนสินค้าคงเหลือไม่พอ", None

    # ลดสต็อกและปรับสถานะ
    target_serial["status"] = "SOLD"
    target_prod["stockQuantity"] -= 1

    # ตรวจสอบการแจ้งเตือนสต็อกต่ำ (< threshold เท่านั้น)
    alert_msg = None
    threshold = target_prod.get("lowStockThreshold", 0)
    current_stock = target_prod["stockQuantity"]

    if current_stock < threshold:
        alert_msg = f"แจ้งเตือน: สินค้า {target_prod['productId']} สต็อกต่ำกว่าเกณฑ์ (คงเหลือ {current_stock} ชิ้น)"
        # เรียก Observer ทุกตัวโดยไม่สนว่าเป็นช่องทางไหน
        self.notify_all(alert_msg)

    self.save_data(data)
    return True, f"ตัดสต็อกสำเร็จ คงเหลือ {current_stock} ชิ้น", alert_msg

def submit_chat_request(self, user_id: str, image_filename: str, staff_online: bool = False):
    valid_exts = [".png", ".jpg", ".jpeg"]
    if not any(image_filename.lower().endswith(ext) for ext in valid_exts):
        return False, "รองรับเฉพาะไฟล์รูปภาพ (.png, .jpg, .jpeg) เท่านั้น"

    data = self.load_data()
    if "chat_requests" not in data:
        data["chat_requests"] = []

    status = "ASSIGNED" if staff_online else "WAITING"
    req_id = f"REQ-{len(data['chat_requests']) + 1:03d}"

    data["chat_requests"].append({
        "requestId": req_id,
        "userId": user_id,
        "image": image_filename,
        "status": status
    })
    self.save_data(data)

    if staff_online:
        return True, f"สร้างคำขอ {req_id} สำเร็จ ส่งต่อให้ช่างเรียบร้อย (เป้าหมายตอบกลับภายใน 1 นาที)"
    return True, f"ขณะนี้ไม่มีผู้เชี่ยวชาญออนไลน์ ระบบได้บันทึกคำขอ {req_id} ไว้แล้ว"

ข้อกำหนด

เพิ่มเมธอด sell_many(orders: dict[str, int]) -> dict[str, int] คืน {ชื่อ: คงเหลือ}
ถ้ามีรายการใดรายการหนึ่ง stock ไม่พอ ต้อง raise ValueError และต้องไม่หักรายการใดเลย ทุกรายการต้องสำเร็จพร้อมกันหรือไม่สำเร็จเลย (atomic)
ใช้ exception แบบเดียวกับเมธอดเดิม (KeyError เมื่อไม่พบสินค้า)
ห้ามใช้ library ภายนอก

โค้ดต้องผ่าน test เหล่านี้

ขายหลายรายการสำเร็จ คืนคงเหลือถูกต้อง
ถ้ารายการที่ 2 stock ไม่พอ ต้องไม่หักรายการที่ 1 (rollback)

**ผลลัพธ์ที่ AI ให้มา:**
ได้ ให้เพิ่ม sell_many() ใน InventoryService โดยหลักคือ ตรวจสอบทุกสินค้าก่อน → ถ้าผ่านทั้งหมดค่อยหัก Stock → save ครั้งเดียว แบบนี้จึงเป็น atomic และไม่ต้อง rollback จริง ๆ
```python
def sell_many(self, orders: dict[str, int]) -> dict[str, int]:
    data = self.load_data()
    products = data.get("products", [])

    # ตรวจสอบสินค้าทั้งหมดก่อนหัก Stock
    targets = {}

    for product_id, quantity in orders.items():
        product = next(
            (p for p in products if p["productId"] == product_id),
            None
        )

        # ใช้ KeyError เมื่อไม่พบสินค้า
        if not product:
            raise KeyError(product_id)

        # ตรวจสอบจำนวนที่สั่งขาย
        if quantity <= 0:
            raise ValueError(f"จำนวนสินค้าต้องมากกว่า 0: {product_id}")

        current_stock = product.get("stockQuantity", 0)

        if current_stock < quantity:
            raise ValueError(
                f"จำนวนสินค้า {product_id} ไม่พอ "
                f"(ต้องการ {quantity}, คงเหลือ {current_stock})"
            )

        targets[product_id] = (product, quantity)

    # ผ่านการตรวจสอบทุกสินค้าแล้ว จึงค่อยหัก Stock
    result = {}

    for product_id, (product, quantity) in targets.items():
        product["stockQuantity"] -= quantity
        result[product_id] = product["stockQuantity"]

        # ตรวจสอบ Low Stock หลังหัก
        threshold = product.get("lowStockThreshold", 0)
        current_stock = product["stockQuantity"]

        if current_stock < threshold:
            alert_msg = (
                f"แจ้งเตือน: สินค้า {product_id} "
                f"สต็อกต่ำกว่าเกณฑ์ (คงเหลือ {current_stock} ชิ้น)"
            )
            self.notify_all(alert_msg)

    # บันทึกครั้งเดียวหลังจากทุกรายการสำเร็จ
    self.save_data(data)

    return result
```

### ทำไมตัวนี้ผ่านเงื่อนไข Atomic

สมมติ Stock เป็น

```python
RAM-A = 10
RAM-B = 2
```

สั่ง:

```python
inventory.sell_many({
    "RAM-A": 3,
    "RAM-B": 5
})
```

ระบบจะตรวจสอบก่อนว่า

```text
RAM-A → มี 10 ต้องการ 3 → ผ่าน
RAM-B → มี 2 ต้องการ 5 → ไม่ผ่าน
```

จึง `raise ValueError` **ก่อนที่จะหัก RAM-A** ทำให้ผลสุดท้ายยังเป็น

```text
RAM-A = 10
RAM-B = 2
```

ไม่มีการ rollback เพราะเรายังไม่ได้แก้ข้อมูลตั้งแต่แรก

ส่วนกรณีสำเร็จ:

```python
result = inventory.sell_many({
    "RAM-A": 3,
    "RAM-B": 1
})
```

จะได้

```python
{
    "RAM-A": 7,
    "RAM-B": 1
}
```

และ `items.json` จะถูก `save_data()` **ครั้งเดียวหลังทุกตัวสำเร็จ** ครับ



---

## สรุปข้อแตกต่าง
รอบที่ 1 (Prompt สั้น):
แม้ AI จะฉลาดพอที่ออกแบบลอจิกแบบ 2-pass (เช็คก่อนค่อยหัก) เพื่อกันปัญหา Atomic ได้ แต่ AI ต้องเดาโครงสร้างข้อมูลเองทั้งหมด (สมมติให้ใช้ self.stock เป็น Dictionary ธรรมดา) โค้ดที่ได้มาจึงเป็นแค่ "ฟังก์ชันลอยๆ" ไม่มีการเซฟลงไฟล์ ไม่มีการดัก KeyError ตามมาตรฐานเดิมของระบบ และไม่สามารถนำมาแปะในคลาส InventoryService เดิมแล้วใช้งานได้ทันที ผู้พัฒนาต้องเสียเวลามาแก้โครงสร้างเองอีกเยอะ

รอบที่ 2 (Prompt ที่แนบ Context ครบถ้วน):
เมื่อเรากำหนด Context (โค้ดเดิม) และ Requirements ที่ชัดเจน AI สามารถสร้างโค้ดที่ "กลมกลืน" กับระบบเดิมได้อย่างสมบูรณ์แบบ:

เข้ากันได้กับโค้ดเดิม (Compatibility): มีการดึงข้อมูลผ่าน self.load_data() และเข้าถึงข้อมูลแบบ List of Dictionaries ได้ถูกต้องเป๊ะ

ทำตามเงื่อนไขเป๊ะ (Constraints): คืนค่าเป็น dict[str, int] ตามที่สั่ง และโยน KeyError เมื่อไม่พบสินค้า

ฟีเจอร์แฝงทำงานครบถ้วน: AI สังเกตเห็นระบบ Observer ในโค้ดเดิม และดึงฟังก์ชัน self.notify_all() มาใช้แจ้งเตือน Low Stock ให้ด้วยโดยที่เราไม่ต้องสั่ง และสั่ง self.save_data() ให้เรียบร้อยในตอนจบ

สรุป: การทำ Context Engineering ช่วยเปลี่ยนจาก "โค้ดตัวอย่างที่ทำงานได้" ให้กลายเป็น "โค้ดระดับ Production ที่เสียบเข้ากับระบบเดิมได้ทันที" และช่วยปิดช่องโหว่เรื่องบั๊กโครงสร้างข้อมูลได้อย่างมีประสิทธิภาพ
