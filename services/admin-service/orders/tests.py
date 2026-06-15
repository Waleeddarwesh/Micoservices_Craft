from decimal import Decimal
from django.test import TestCase
from django.utils import timezone
from accounts.models import User, Address, Supplier
from products.models import Product, Category
from orders.models import Warehouse, Cart, CartItems, Order, Shipment
from orders.services import create_order_from_cart, _process_payments
from returnrequest.models import Transaction
from Handcrafts.business_config import (
    PLATFORM_PRODUCT_COMMISSION, SUPPLIER_PRODUCT_REVENUE, 
    PLATFORM_DELIVERY_MARGIN, DRIVER_DELIVERY_REVENUE, DEFAULT_CASHBACK_RATE
)

class DeliveryAndFinancialTests(TestCase):
    def setUp(self):
        # 1. Create Platform User
        self.craft_user = User.objects.create(
            email="CraftEG@craft.com", 
            first_name="Craft",
            last_name="Admin",
            Balance=Decimal('0.00'),
            is_staff=True,
            is_superuser=True
        )
        
        # 2. Create Customers and Suppliers
        self.customer = User.objects.create(email="customer@test.com", first_name="Cust", last_name="Omer", Balance=Decimal('1000.00'), is_customer=True)
        
        self.supplier1_user = User.objects.create(email="supplier1@test.com", first_name="Sup", last_name="One", Balance=Decimal('0.00'), is_supplier=True)
        self.supplier1 = Supplier.objects.create(user=self.supplier1_user)
        
        self.supplier2_user = User.objects.create(email="supplier2@test.com", first_name="Sup", last_name="Two", Balance=Decimal('0.00'), is_supplier=True)
        self.supplier2 = Supplier.objects.create(user=self.supplier2_user)
        
        # 3. Create Addresses
        self.cairo_address = Address.objects.create(user=self.customer, State="Cairo", City="Nasr City", Street="Street 1")
        # Supplier 1 is in Cairo
        Address.objects.create(user=self.supplier1_user, State="Cairo", City="Maadi", Street="Street 2")
        # Supplier 2 is in Alexandria
        Address.objects.create(user=self.supplier2_user, State="Alexandria", City="Smouha", Street="Street 3")
        
        # 4. Create Warehouses
        self.cairo_warehouse = Warehouse.objects.create(
            name="Cairo", Address=self.cairo_address, delivery_fee=Decimal('50.00')
        )
        self.alex_warehouse = Warehouse.objects.create(
            name="Alexandria", Address=Address.objects.filter(State="Alexandria").first(), delivery_fee=Decimal('70.00')
        )
        
        # 5. Create Products
        self.category = Category.objects.create(Title="Crafts", Slug="crafts")
        self.product1 = Product.objects.create(
            ProductName="Cairo Pot", Supplier=self.supplier1, Category=self.category,
            UnitPrice=Decimal('100.00'), Stock=10, UnitWeight=1.0
        )
        self.product2 = Product.objects.create(
            ProductName="Alex Rug", Supplier=self.supplier2, Category=self.category,
            UnitPrice=Decimal('200.00'), Stock=10, UnitWeight=1.0
        )
        
        # 6. Create Cart
        self.cart = Cart.objects.create(User=self.customer)

    def test_same_state_order_and_financials(self):
        """Test Case 1: Same State Delivery (Cairo Customer -> Cairo Supplier)"""
        CartItems.objects.create(CartID=self.cart, Product=self.product1, Quantity=1)
        
        order = create_order_from_cart(
            user=self.customer, cart=self.cart, address_id=self.cairo_address.id,
            coupon_code=None, payment_method=Order.PaymentMethod.BALANCE, is_paid=True
        )
        
        # Verify Shipments (1 local shipment expected)
        shipments = Shipment.objects.filter(order=order)
        self.assertEqual(shipments.count(), 1)
        shipment = shipments.first()
        self.assertEqual(shipment.from_state, "Cairo")
        self.assertEqual(shipment.to_state, "Cairo")
        self.assertEqual(shipment.status, Shipment.ShipmentStatus.CREATED)
        
        # Verify Order Totals (Product: 100, Delivery: 50)
        self.assertEqual(order.delivery_fee, Decimal('50.00'))
        self.assertEqual(order.final_amount, Decimal('150.00'))
        
        # Verify Customer Balance Deduction and Cashback
        self.customer.refresh_from_db()
        expected_cashback = order.final_amount * DEFAULT_CASHBACK_RATE
        # 1000 - 150 + (150*0.02 = 3.00) = 853.00
        self.assertEqual(self.customer.Balance, Decimal('853.00'))
        
        # Simulate Driver Delivery to trigger payments
        driver_user = User.objects.create(email="driver1@test.com", first_name="Drive", last_name="One", Balance=Decimal('0.00'), is_delivery=True)
        _process_payments(driver_user, shipment, self.cairo_warehouse)
        
        self.supplier1_user.refresh_from_db()
        self.craft_user.refresh_from_db()
        driver_user.refresh_from_db()
        
        # Supplier Revenue = 100 * 0.85 = 85.00
        self.assertEqual(self.supplier1_user.Balance, Decimal('85.00'))
        
        # Driver Revenue = 50 * 0.88 = 44.00
        self.assertEqual(driver_user.Balance, Decimal('44.00'))
        
        # Platform Revenue:
        # Initially received 150.00 from BALANCE payment
        # Distributed 85 to supplier and 44 to driver
        # Final platform balance should be 150 - 85 - 44 = 21.00
        # (15 for product commission, 6 for delivery commission)
        self.assertEqual(self.craft_user.Balance, Decimal('21.00'))

    def test_inter_state_order_routing(self):
        """Test Case 2: Different State Delivery (Cairo Customer -> Alexandria Supplier)"""
        CartItems.objects.create(CartID=self.cart, Product=self.product2, Quantity=1)
        
        order = create_order_from_cart(
            user=self.customer, cart=self.cart, address_id=self.cairo_address.id,
            coupon_code=None, payment_method=Order.PaymentMethod.CASH_ON_DELIVERY
        )
        
        # Verify Shipments (2 shipments expected for inter-state)
        shipments = Shipment.objects.filter(order=order)
        self.assertEqual(shipments.count(), 2)
        
        # 1st Hop: Supplier (Alex) -> Cairo Warehouse (CREATED)
        hop1 = shipments.get(status=Shipment.ShipmentStatus.CREATED)
        self.assertEqual(hop1.from_state, "Alexandria")
        self.assertEqual(hop1.to_state, "Cairo")
        
        # 2nd Hop: Alex Warehouse -> Cairo Customer (In_Transmit)
        hop2 = shipments.get(status=Shipment.ShipmentStatus.In_Transmit)
        self.assertEqual(hop2.from_state, "Alexandria")
        self.assertEqual(hop2.to_state, "Cairo")
        
        # Verify Totals
        # Product: 200, Delivery: Cairo(50) + Alex(70) + Surcharge(20) = 140
        self.assertEqual(order.delivery_fee, Decimal('140.00'))
        self.assertEqual(order.final_amount, Decimal('340.00'))

    def test_cod_financial_enforcement(self):
        """Test Case 4: Cash On Delivery Financial Splits"""
        CartItems.objects.create(CartID=self.cart, Product=self.product1, Quantity=1)
        
        order = create_order_from_cart(
            user=self.customer, cart=self.cart, address_id=self.cairo_address.id,
            coupon_code=None, payment_method=Order.PaymentMethod.CASH_ON_DELIVERY
        )
        
        shipment = Shipment.objects.get(order=order)
        driver_user = User.objects.create(email="driver2@test.com", first_name="Drive", last_name="Two", Balance=Decimal('0.00'), is_delivery=True)
        
        _process_payments(driver_user, shipment, self.cairo_warehouse)
        
        self.supplier1_user.refresh_from_db()
        self.craft_user.refresh_from_db()
        driver_user.refresh_from_db()
        
        # COD means driver collected physical cash (100 product + 50 delivery = 150)
        # Driver should be debited Product Cost (100) + Platform Delivery Commission (50 * 0.12 = 6)
        # Total Driver Debit = -106.00
        # This leaves driver with net 44 EGP cash profit (88% of 50).
        self.assertEqual(driver_user.Balance, Decimal('-106.00'))
        
        # Supplier still gets virtual credit of 85.00
        self.assertEqual(self.supplier1_user.Balance, Decimal('85.00'))
        
        # Platform still gets virtual credit of Product Comm (15.00) + Del Comm (6.00) = 21.00
        self.assertEqual(self.craft_user.Balance, Decimal('21.00'))
