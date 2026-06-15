import pytest
from django.urls import reverse
from rest_framework import status
from tests.factories import ProductFactory, CartFactory, OrderFactory
from orders.models import Cart, Order

@pytest.mark.django_db
def test_customer_can_add_item_to_cart(customer_client, customer_user):
    product = ProductFactory(Stock=10)
    
    # Ensure cart exists
    cart, _ = Cart.objects.get_or_create(User=customer_user)
    
    url = reverse('cartitem-list')
    data = {
        "CartID": cart.id,
        "Product_id": product.id,
        "Quantity": 2
    }
    
    response = customer_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['Quantity'] == 2

@pytest.mark.django_db
def test_customer_can_create_order(customer_client, customer_user, dummy_address):
    from accounts.models import Address
    product = ProductFactory(Stock=10)
    Address.objects.create(user=product.Supplier.user, Street="S St", City="S City", State="Cairo")
    from orders.models import Warehouse
    warehouse_address = Address.objects.create(user=customer_user, Street="WH St", City="WH City", State="Cairo")
    Warehouse.objects.create(name="Cairo", Address=warehouse_address, delivery_fee=50.0)
    cart, _ = Cart.objects.get_or_create(User=customer_user)
    from orders.models import CartItems
    CartItems.objects.create(CartID=cart, Product=product, Quantity=1)
    
    url = reverse('order-list')
    data = {
        "address_id": dummy_address.id,
        "payment_method": "Cash on Delivery"
    }
    
    response = customer_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_201_CREATED, response.data
    assert "successfully" in response.data['message']
    assert Order.objects.filter(user=customer_user).exists()
