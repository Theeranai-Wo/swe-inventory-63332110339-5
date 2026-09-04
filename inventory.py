from abc import ABC, abstractmethod
import json
import os

DATA_FILE = "items.json"

# ==========================================
# Observer Pattern: Notifier Interface & Implementations
# ==========================================
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

# ==========================================
# Factory Pattern: NotifierFactory
# ==========================================
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

# ==========================================
# Core Domain & InventoryService (DIP + Observer Subject)
# ==========================================
class InventoryService:
    def __init__(self, observers: list[BaseNotifier] = None):
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
