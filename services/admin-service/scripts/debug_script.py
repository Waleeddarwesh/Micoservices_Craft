import os
import django
import sys
import json
from decimal import Decimal

# Set up Django environment
sys.path.append('d:/Craft/Handcrafts')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Handcrafts.settings')
django.setup()

from rest_framework.test import APIClient
from accounts.models import User, Address
from orders.models import Cart, CartItems
from products.models import Product, Category
from tests.factories import ProductFactory, CustomerFactory, SupplierFactory
from django.core.files.uploadedfile import SimpleUploadedFile

# Create test data
customer = CustomerFactory()
customer_user = customer.user

dummy_address = Address.objects.create(
    user=customer_user,
    Street="123 Test St",
    City="Cairo",
    State="Cairo"
)

product = ProductFactory(Stock=10, UnitPrice=Decimal('150.00'))
Address.objects.create(user=product.Supplier.user, Street="S St", City="S City", State="Cairo")

cart, _ = Cart.objects.get_or_create(User=customer_user)
CartItems.objects.create(CartID=cart, Product=product, Quantity=1)

# Test order creation
client = APIClient()
client.force_authenticate(user=customer_user)

print("--- Test Order Creation ---")
data = {
    "address_id": dummy_address.id,
    "payment_method": "Cash on Delivery"
}
response = client.post('/orders/orders/', data, format='json')
print(f"Status Code: {response.status_code}")
print(f"Response Body: {response.data}")

print("\n--- Test Payment Intent ---")
payment_data = {
    "address_id": dummy_address.id
}
response = client.post('/payment/order-payment/process_order_payment/', payment_data, format='json')
print(f"Status Code: {response.status_code}")
print(f"Response Body: {response.data}")

print("\n--- Test Product Creation ---")
supplier = SupplierFactory()
supplier_user = supplier.user
client.force_authenticate(user=supplier_user)
category = Category.objects.create(CategoryName="Test", isActive=True)

image = SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")
product_data = {
    'ProductName': 'Test Product',
    'Description': 'Test Description',
    'UnitPrice': '100.00',
    'Stock': 10,
    'Category': category.id,
    'uploaded_images': [image],
    'uploaded_Colors': ['Red'],
    'uploaded_Sizes': ['M']
}
response = client.post('/products/products/', product_data, format='multipart')
print(f"Status Code: {response.status_code}")
print(f"Response Body: {response.data}")

