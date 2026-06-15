# Handcrafts/business_config.py
from decimal import Decimal, ROUND_HALF_UP

# =========================
# Financial Precision
# =========================
MONEY_DECIMAL_PLACES = Decimal("0.01")

# =========================
# Product Marketplace Margins
# =========================
PLATFORM_PRODUCT_COMMISSION = Decimal("0.15")
SUPPLIER_PRODUCT_REVENUE = Decimal("0.85")

# =========================
# Delivery & Logistics Margins
# =========================
PLATFORM_DELIVERY_MARGIN = Decimal("0.12")
DRIVER_DELIVERY_REVENUE = Decimal("0.88")

# =========================
# Course / Digital Goods Margins
# =========================
PLATFORM_COURSE_COMMISSION = Decimal("0.30")
INSTRUCTOR_COURSE_REVENUE = Decimal("0.70")

# =========================
# Customer Loyalty / Cashback
# =========================
DEFAULT_CASHBACK_RATE = Decimal("0.02")

# =========================
# Shipping Rules
# =========================
INTER_STATE_SHIPPING_SURCHARGE = Decimal("20.00")

# =========================
# Delivery Bonuses
# =========================
GOLD_TIER_DELIVERY_BONUS = Decimal("0.15")
SILVER_TIER_DELIVERY_BONUS = Decimal("0.05")

# =========================
# Calculation Helpers
# =========================
def money(value: Decimal) -> Decimal:
    """Rounds money to two decimal places."""
    return value.quantize(MONEY_DECIMAL_PLACES, rounding=ROUND_HALF_UP)

def calculate_product_split(product_total: Decimal) -> dict:
    """Returns the split for product sales."""
    return {
        "platform_commission": money(product_total * PLATFORM_PRODUCT_COMMISSION),
        "supplier_revenue": money(product_total * SUPPLIER_PRODUCT_REVENUE),
    }

def calculate_delivery_split(delivery_fee: Decimal) -> dict:
    """Returns the split for delivery fees."""
    return {
        "platform_margin": money(delivery_fee * PLATFORM_DELIVERY_MARGIN),
        "driver_revenue": money(delivery_fee * DRIVER_DELIVERY_REVENUE),
    }

def calculate_course_split(course_price: Decimal) -> dict:
    """Returns the split for digital course purchases."""
    return {
        "platform_commission": money(course_price * PLATFORM_COURSE_COMMISSION),
        "instructor_revenue": money(course_price * INSTRUCTOR_COURSE_REVENUE),
    }

def calculate_cashback(order_final_amount: Decimal) -> Decimal:
    """Returns the customer cashback amount based on final order value."""
    return money(order_final_amount * DEFAULT_CASHBACK_RATE)
