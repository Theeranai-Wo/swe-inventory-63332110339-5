import pytest

from inventory import Inventory


def test_low_stock_items_all_above_threshold():
    """กรณีที่ 1: สินค้าทุกรายการมีจำนวนมากกว่า threshold -> คืน list ว่าง"""
    inv = Inventory()
    inv.add_item("Apple", 10, 15.0)
    inv.add_item("Banana", 20, 10.0)
    assert inv.low_stock_items(5) == []


def test_low_stock_items_exact_threshold():
    """กรณีที่ 2: มีสินค้าที่จำนวนเท่ากับ threshold พอดี -> ต้องถูกนับรวมด้วย"""
    inv = Inventory()
    inv.add_item("Apple", 5, 15.0)
    inv.add_item("Banana", 10, 10.0)
    assert inv.low_stock_items(5) == ["Apple"]


def test_low_stock_items_multiple_items_sorted_by_name():
    """กรณีที่ 3: มีสินค้าเข้าเกณฑ์หลายรายการ -> ผลลัพธ์เรียงตามชื่อ ไม่ใช่ตามลำดับที่เพิ่ม"""
    inv = Inventory()
    inv.add_item("Zebra", 2, 50.0)
    inv.add_item("Apple", 3, 15.0)
    inv.add_item("Mango", 1, 25.0)
    inv.add_item("Orange", 10, 20.0)  # รายการนี้เกิน threshold ไม่ควรติดมา
    assert inv.low_stock_items(5) == ["Apple", "Mango", "Zebra"]


def test_low_stock_items_empty_inventory():
    """กรณีที่ 4: คลังว่าง -> คืน list ว่าง ไม่ใช่ error"""
    inv = Inventory()
    assert inv.low_stock_items(10) == []


def test_low_stock_items_threshold_zero():
    """กรณีที่ 5: threshold เป็น 0 -> คืนเฉพาะสินค้าที่เหลือ 0"""
    inv = Inventory()
    inv.add_item("ZeroItem", 0, 10.0)
    inv.add_item("SomeItem", 1, 10.0)
    assert inv.low_stock_items(0) == ["ZeroItem"]


def test_low_stock_items_threshold_negative():
    """กรณีที่ 6: threshold ติดลบ -> คืน list ว่าง เนื่องจากจำนวนสินค้าไม่สามารถติดลบได้"""
    inv = Inventory()
    inv.add_item("ZeroItem", 0, 10.0)
    inv.add_item("SomeItem", 5, 10.0)
    assert inv.low_stock_items(-1) == []


# ==============================================================================
# ขั้นที่ 4: Unit Tests สำหรับเมธอด sell (AI Test + ส่วนเสริม Edge Cases 4 กลุ่ม)
# ==============================================================================

def test_sell_normal_ai_generated():
    """กรณีปกติที่ AI มักจะเขียนให้: ขายสินค้าได้สำเร็จ และยอดคงเหลือลดลงถูกต้อง"""
    inv = Inventory()
    inv.add_item("Apple", 10, 15.0)
    remaining = inv.sell("Apple", 3)
    assert remaining == 7


def test_sell_boundary_exact_remaining_stock():
    """กลุ่มที่ 1 ค่าขอบ: ขายเท่ากับจำนวนที่เหลือทั้งหมด -> ต้องสำเร็จและคงเหลือ 0 พอดี"""
    inv = Inventory()
    inv.add_item("Apple", 10, 15.0)
    remaining = inv.sell("Apple", 10)
    assert remaining == 0


def test_sell_invalid_zero_amount():
    """กลุ่มที่ 2 ค่าที่ไม่ควรรับ: ขายจำนวน 0 -> ต้อง raise ValueError"""
    inv = Inventory()
    inv.add_item("Apple", 10, 15.0)
    with pytest.raises(ValueError, match="จำนวนที่ขายต้องมากกว่าศูนย์"):
        inv.sell("Apple", 0)


def test_sell_invalid_negative_amount():
    """กลุ่มที่ 2 ค่าที่ไม่ควรรับ: ขายจำนวนติดลบ -> ต้อง raise ValueError"""
    inv = Inventory()
    inv.add_item("Apple", 10, 15.0)
    with pytest.raises(ValueError, match="จำนวนที่ขายต้องมากกว่าศูนย์"):
        inv.sell("Apple", -5)


def test_sell_invalid_exceeds_stock():
    """กลุ่มที่ 2 ค่าที่ไม่ควรรับ: ขายเกินจำนวนคงเหลือ -> ต้อง raise ValueError พร้อมข้อความระบุชัดเจน"""
    inv = Inventory()
    inv.add_item("Apple", 5, 15.0)
    with pytest.raises(ValueError, match="ไม่เพียงพอสำหรับการขาย"):
        inv.sell("Apple", 6)


def test_sell_error_item_not_found():
    """กลุ่มที่ 3 เส้นทาง error: ขายสินค้าที่ไม่มีในคลัง -> ต้อง raise KeyError พร้อมข้อความถูกต้อง"""
    inv = Inventory()
    inv.add_item("Apple", 10, 15.0)
    with pytest.raises(KeyError, match="ไม่พบสินค้า 'Orange' ในระบบ"):
        inv.sell("Orange", 2)


def test_sell_invalid_type_string():
    """กลุ่มที่ 4 ชนิดข้อมูล: ส่งจำนวนเป็นข้อความ (str) -> ต้อง raise TypeError"""
    inv = Inventory()
    inv.add_item("Apple", 10, 15.0)
    with pytest.raises(TypeError, match="จำนวนที่ขายต้องเป็นจำนวนเต็มเท่านั้น"):
        inv.sell("Apple", "three")


def test_sell_invalid_type_float():
    """กลุ่มที่ 4 ชนิดข้อมูล: ส่งจำนวนเป็นทศนิยม (float) -> ต้อง raise TypeError"""
    inv = Inventory()
    inv.add_item("Apple", 10, 15.0)
    with pytest.raises(TypeError, match="จำนวนที่ขายต้องเป็นจำนวนเต็มเท่านั้น"):
        inv.sell("Apple", 2.5)
