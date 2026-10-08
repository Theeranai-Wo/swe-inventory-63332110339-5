"""โมดูลคำนวณราคาและส่วนลดของระบบ Inventory (ฉบับ Refactored)

ได้รับการปรับปรุงโครงสร้างจาก pricing_legacy.py เพื่อแก้ปัญหา Code Smells:
1. กำหนดค่าคงที่แทน Magic Numbers ชัดเจน
2. แยกฟังก์ชันย่อยตามหลัก Single Responsibility Principle (SRP)
3. ปรับปรุงชื่อตัวแปรให้สื่อความหมาย (Descriptive Naming)
4. ปรับการเปรียบเทียบค่า None ตามมาตรฐาน PEP 8 (ใช้ is / is not)
5. รักษาพฤติกรรมการคำนวณเดิม 100% (Backward Compatibility)
"""

import datetime
from typing import Any

# ==============================================================================
# ค่าคงที่สำหรับการคำนวณ (Constants)
# ==============================================================================
TAX_RATE = 0.07

# เกณฑ์และอัตราส่วนลดสำหรับการซื้อจำนวนมาก
BULK_THRESHOLD_HIGH = 100
BULK_DISCOUNT_HIGH_FACTOR = 0.90  # ลด 10%
BULK_THRESHOLD_MID = 50
BULK_DISCOUNT_MID_FACTOR = 0.95   # ลด 5%

# อัตราส่วนลดและแต้มสะสมของสมาชิก
MEMBER_DISCOUNT_FACTOR = 0.95      # สมาชิกลด 5%
POINTS_SPENDING_DIVISOR = 100      # 1 แต้มต่อยอดใช้จ่าย 100 บาท

# คูปองส่วนลด
COUPON_SAVE50_AMOUNT = 50.0        # ลด 50 บาท
COUPON_HALF_FACTOR = 0.50          # ลด 50%
COUPON_NEWYEAR_FACTOR = 0.80       # ลด 20%
NEWYEAR_ELIGIBLE_MONTH = 1         # เดือนมกราคม

# สถานะคงค้างเดิม (รองรับระบบเดิมที่เรียกใช้งานตัวแปรระดับโมดูล)
member_points: dict[str, int] = {}
LOG: list[tuple[str | None, float]] = []


# ==============================================================================
# ฟังก์ชันย่อยตามหน้าที่ (Single Responsibility Functions)
# ==============================================================================
def calculate_item_subtotal(quantity: int, unit_price: float) -> float:
    """คำนวณราคาย่อยของสินค้าแต่ละรายการพร้อมคิดส่วนลดการซื้อปริมาณมาก"""
    if quantity <= 0:
        return 0.0

    raw_subtotal = quantity * unit_price
    if quantity >= BULK_THRESHOLD_HIGH:
        return raw_subtotal * BULK_DISCOUNT_HIGH_FACTOR
    elif quantity >= BULK_THRESHOLD_MID:
        return raw_subtotal * BULK_DISCOUNT_MID_FACTOR

    return raw_subtotal


def calculate_cart_subtotal(items: list[tuple[str, int, float] | Any]) -> float:
    """คำนวณราคารวมก่อนส่วนลดและภาษีของสินค้าทั้งหมดในตะกร้า"""
    total = 0.0
    for item in items:
        # กระจายค่าจาก tuple เพื่อความชัดเจนและป้องกัน positional confusion
        _name, quantity, unit_price = item[0], item[1], item[2]
        total += calculate_item_subtotal(quantity, unit_price)
    return total


def apply_member_benefits(total: float, member: str | None) -> float:
    """ประมวลผลส่วนลดสมาชิกและคำนวณแต้มสะสม"""
    if member is None:
        return total

    if member not in member_points:
        member_points[member] = 0

    discounted_total = total * MEMBER_DISCOUNT_FACTOR
    earned_points = int(discounted_total / POINTS_SPENDING_DIVISOR)
    member_points[member] += earned_points

    return discounted_total


def apply_coupon_discount(
    total: float, coupon: str | None, today: datetime.date | None = None
) -> float:
    """คำนวณส่วนลดจากคูปองตามเงื่อนไขที่กำหนด"""
    if coupon is None:
        return total

    if coupon == "SAVE50":
        total -= COUPON_SAVE50_AMOUNT
    elif coupon == "HALF":
        total *= COUPON_HALF_FACTOR
    elif coupon == "NEWYEAR":
        current_date = today if today is not None else datetime.date.today()
        if current_date.month == NEWYEAR_ELIGIBLE_MONTH:
            total *= COUPON_NEWYEAR_FACTOR

    return total


def calculate_final_amount(total: float, tax_rate: float = TAX_RATE) -> float:
    """คำนวณยอดเงินสุดท้ายหลังรวมภาษีและปัดเศษทศนิยม 2 ตำแหน่ง"""
    # หากส่วนลดมากกว่ายอดรวม ยอดต้องไม่ติดลบ
    non_negative_total = max(0.0, total)
    total_with_tax = non_negative_total + (non_negative_total * tax_rate)
    return round(total_with_tax, 2)


# ==============================================================================
# ฟังก์ชันหลัก (Main Calculation Entry Point)
# ==============================================================================
def calc(
    items: list[tuple[str, int, float]],
    member: str | None = None,
    coupon: str | None = None,
    today: datetime.date | None = None,
) -> float:
    """คำนวณราคาสุทธิของสินค้าพร้อมส่วนลด สมาชิก คูปอง และภาษี (เหมือนเดิม 100%)"""
    total = calculate_cart_subtotal(items)
    total = apply_member_benefits(total, member)
    total = apply_coupon_discount(total, coupon, today)
    final_amount = calculate_final_amount(total)

    LOG.append((member, final_amount))
    return final_amount
