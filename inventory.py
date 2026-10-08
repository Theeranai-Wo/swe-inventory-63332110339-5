# inventory.py  -- โค้ดจาก Lab 3/4

class InventoryItem:
    def __init__(self, name: str, quantity: int, price: float):
        if not name or not name.strip():
            raise ValueError("ชื่อสินค้าต้องไม่ว่างเปล่า")
        if quantity < 0:
            raise ValueError("จำนวนสินค้าต้องไม่ติดลบ")
        if price <= 0:
            raise ValueError("ราคาต้องมากกว่าศูนย์")
        self.name = name.strip()
        self.quantity = quantity
        self.price = price


class Inventory:
    def __init__(self):
        self._items: dict[str, InventoryItem] = {}

    def add_item(self, name: str, quantity: int, price: float) -> InventoryItem:
        """เพิ่มสินค้าใหม่ ถ้าชื่อซ้ำให้ raise ValueError"""
        if name in self._items:
            raise ValueError(f"สินค้า '{name}' มีอยู่ในระบบแล้ว")
        item = InventoryItem(name, quantity, price)
        self._items[name] = item
        return item

    def restock(self, name: str, amount: int) -> int:
        """เพิ่มจำนวนสินค้าที่มีอยู่ คืนค่าจำนวนหลังเติม"""
        if name not in self._items:
            raise KeyError(f"ไม่พบสินค้า '{name}' ในระบบ")
        if amount <= 0:
            raise ValueError("จำนวนที่เติมต้องมากกว่าศูนย์")
        self._items[name].quantity += amount
        return self._items[name].quantity

    def sell(self, name: str, amount: int) -> int:
        """ขายสินค้า ลดจำนวน คืนค่าจำนวนคงเหลือ"""
        if name not in self._items:
            raise KeyError(f"ไม่พบสินค้า '{name}' ในระบบ")
        if not isinstance(amount, int) or isinstance(amount, bool):
            raise TypeError("จำนวนที่ขายต้องเป็นจำนวนเต็มเท่านั้น")
        if amount <= 0:
            raise ValueError("จำนวนที่ขายต้องมากกว่าศูนย์")
        if self._items[name].quantity < amount:
            raise ValueError(
                f"สินค้า '{name}' คงเหลือ {self._items[name].quantity} ชิ้น "
                f"ไม่เพียงพอสำหรับการขาย {amount} ชิ้น"
            )
        self._items[name].quantity -= amount
        return self._items[name].quantity

    def get_total_value(self) -> float:
        """คำนวณมูลค่ารวมของสินค้าทั้งหมดในคลัง"""
        return sum(
            item.quantity * item.price for item in self._items.values()
        )

    def low_stock_items(self, threshold: int) -> list[str]:
        """คืนรายชื่อสินค้าที่มีจำนวนคงเหลือ น้อยกว่าหรือเท่ากับ threshold โดยเรียงตามชื่อ"""
        low_stock_names = [
            item.name for item in self._items.values()
            if item.quantity <= threshold
        ]
        return sorted(low_stock_names)
