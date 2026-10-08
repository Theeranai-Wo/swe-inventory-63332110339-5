import datetime

import pytest

import pricing as pricing_legacy


@pytest.fixture(autouse=True)
def reset_legacy_state():
    """ล้างสถานะ Global mutable state ก่อนและหลังการรันแต่ละ test เพื่อป้องกัน state leakage"""
    pricing_legacy.member_points.clear()
    pricing_legacy.LOG.clear()
    yield
    pricing_legacy.member_points.clear()
    pricing_legacy.LOG.clear()


# ==============================================================================
# 1. กลุ่มราคาปกติ (Normal Price)
# ==============================================================================
def test_calc_normal_price_single_item():
    """สินค้าหนึ่งรายการ จำนวนน้อย ไม่ใช้สิทธิ์สมาชิกหรือคูปองใดๆ"""
    items = [("Pen", 2, 10.0)]
    total = pricing_legacy.calc(items)
    # 2 * 10 = 20.0, ภาษี 7% = 1.4 -> 21.4
    assert total == 21.4
    assert pricing_legacy.LOG == [(None, 21.4)]


# ==============================================================================
# 2. กลุ่มซื้อจำนวนมาก (Bulk Purchase Thresholds)
# ==============================================================================
def test_calc_bulk_purchase_below_first_threshold():
    """จำนวน 49 ชิ้น (ยังไม่ถึงเกณฑ์ลดราคา 50 ชิ้น)"""
    items = [("Pen", 49, 10.0)]
    total = pricing_legacy.calc(items)
    # 49 * 10 = 490, ภาษี 7% = 34.3 -> 524.3
    assert total == 524.3


def test_calc_bulk_purchase_exact_fifty_threshold():
    """จำนวน 50 ชิ้นพอดี -> ได้รับส่วนลด 5% (คูณ 0.95)"""
    items = [("Pen", 50, 10.0)]
    total = pricing_legacy.calc(items)
    # 50 * 10 * 0.95 = 475, ภาษี 7% = 33.25 -> 508.25
    assert total == 508.25


def test_calc_bulk_purchase_ninety_nine_threshold():
    """จำนวน 99 ชิ้น (เกณฑ์สูงสุดของลด 5%)"""
    items = [("Pen", 99, 10.0)]
    total = pricing_legacy.calc(items)
    # 99 * 10 * 0.95 = 940.5, บวกภาษี 7% = 1006.335 -> round = 1006.34
    assert total == 1006.34


def test_calc_bulk_purchase_exact_hundred_threshold():
    """จำนวน 100 ชิ้นพอดี -> ได้รับส่วนลด 10% (คูณ 0.90)"""
    items = [("Pen", 100, 10.0)]
    total = pricing_legacy.calc(items)
    # 100 * 10 * 0.90 = 900, บวกภาษี 7% = 63.0 -> 963.0
    assert total == 963.0


# ==============================================================================
# 3. กลุ่มจำนวนเป็นศูนย์ (Quantity Zero)
# ==============================================================================
def test_calc_zero_quantity_single_item():
    """สินค้าที่ใส่จำนวน 0 ชิ้น -> ยอดต้องเป็น 0.0"""
    items = [("Pen", 0, 10.0)]
    total = pricing_legacy.calc(items)
    assert total == 0.0


def test_calc_zero_quantity_mixed_items():
    """มีทั้งสินค้าที่ใส่จำนวน 0 และสินค้าปกติ -> ข้ามรายการจำนวน 0"""
    items = [("Pen", 0, 10.0), ("Book", 1, 100.0)]
    total = pricing_legacy.calc(items)
    # Book: 100 * 1.07 = 107.0
    assert total == 107.0


# ==============================================================================
# 4. กลุ่มสมาชิก (Member Discount & Point Accumulation)
# ==============================================================================
def test_calc_member_new_customer():
    """สมาชิกใหม่: ได้รับส่วนลด 5% และสะสมแต้ม 1 แต้มต่อ 100 บาท"""
    items = [("Book", 1, 200.0)]
    total = pricing_legacy.calc(items, member="Alice")
    # 200 * 0.95 = 190, แต้ม = int(190 / 100) = 1 แต้ม
    # บวกภาษี 7% = 190 * 1.07 = 203.3
    assert total == 203.3
    assert pricing_legacy.member_points["Alice"] == 1
    assert pricing_legacy.LOG == [("Alice", 203.3)]


def test_calc_member_accumulates_existing_points():
    """สมาชิกเดิมที่มีแต้มอยู่แล้ว: แต้มใหม่ต้องบวกสะสมเพิ่มจากของเดิม"""
    pricing_legacy.member_points["Bob"] = 5
    items = [("Book", 1, 200.0)]
    total = pricing_legacy.calc(items, member="Bob")
    # แต้มเพิ่ม 1 แต้ม: 5 + 1 = 6
    assert total == 203.3
    assert pricing_legacy.member_points["Bob"] == 6


# ==============================================================================
# 5. กลุ่มคูปอง (Coupons: SAVE50, HALF, NEWYEAR)
# ==============================================================================
def test_calc_coupon_save50():
    """คูปอง 'SAVE50' -> ลดทันที 50 บาทก่อนคิดภาษี"""
    items = [("Book", 1, 100.0)]
    total = pricing_legacy.calc(items, coupon="SAVE50")
    # (100 - 50) * 1.07 = 53.5
    assert total == 53.5


def test_calc_coupon_half():
    """คูปอง 'HALF' -> ลด 50% ก่อนคิดภาษี"""
    items = [("Book", 1, 100.0)]
    total = pricing_legacy.calc(items, coupon="HALF")
    # (100 * 0.5) * 1.07 = 53.5
    assert total == 53.5


def test_calc_coupon_newyear_in_january():
    """คูปอง 'NEWYEAR' ในเดือนมกราคม -> ลด 20% (คูณ 0.8) ก่อนคิดภาษี"""
    items = [("Book", 1, 100.0)]
    january_date = datetime.date(2026, 1, 15)
    total = pricing_legacy.calc(items, coupon="NEWYEAR", today=january_date)
    # (100 * 0.8) * 1.07 = 85.6
    assert total == 85.6


def test_calc_coupon_newyear_outside_january():
    """คูปอง 'NEWYEAR' นอกเดือนมกราคม -> ไม่ได้รับส่วนลด"""
    items = [("Book", 1, 100.0)]
    february_date = datetime.date(2026, 2, 1)
    total = pricing_legacy.calc(items, coupon="NEWYEAR", today=february_date)
    # 100 * 1.07 = 107.0
    assert total == 107.0


# ==============================================================================
# 6. กลุ่มยอดติดลบ (Negative Subtotal / Discount Exceeds Total)
# ==============================================================================
def test_calc_discount_exceeds_price():
    """ส่วนลดมากกว่าราคาสินค้า -> ยอดรวมก่อนภาษีต้องถูกปรับเป็น 0.0 (ไม่ติดลบ)"""
    items = [("Pen", 1, 20.0)]
    # ลด 50 บาท จาก 20 บาท -> 20 - 50 = -30 -> ปรับเป็น 0.0
    total = pricing_legacy.calc(items, coupon="SAVE50")
    assert total == 0.0
    assert pricing_legacy.LOG == [(None, 0.0)]


# ==============================================================================
# 7. กลุ่มค่าที่ฟังก์ชันเก็บไว้ (Stored State: member_points and LOG)
# ==============================================================================
def test_calc_state_tracking_multiple_calls():
    """ตรวจสอบว่า member_points และ LOG บันทึกประวัติสะสมต่อเนื่องถูกต้อง"""
    items1 = [("Pen", 1, 100.0)]
    items2 = [("Book", 1, 200.0)]

    t1 = pricing_legacy.calc(items1, member="Charlie")
    t2 = pricing_legacy.calc(items2, member="Charlie")

    # t1: 100 * 0.95 = 95 -> points +0, total = 95 * 1.07 = 101.65
    # t2: 200 * 0.95 = 190 -> points +1, total = 190 * 1.07 = 203.3
    assert t1 == 101.65
    assert t2 == 203.3
    assert pricing_legacy.member_points["Charlie"] == 1
    assert pricing_legacy.LOG == [("Charlie", 101.65), ("Charlie", 203.3)]
