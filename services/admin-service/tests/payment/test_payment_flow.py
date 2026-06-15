import pytest
from django.urls import reverse
from rest_framework import status
from unittest.mock import patch
from tests.factories import OrderFactory

@pytest.mark.django_db
@patch('payment.views.stripe.checkout.Session.create')
def test_create_payment_intent(mock_create, customer_client, dummy_address, customer_user):
    mock_create.return_value = type('obj', (object,), {"id": "cs_test_123", "url": "https://checkout.stripe.com/pay/cs_test_123"})
    
    from orders.models import Cart, CartItems
    from accounts.models import Address
    from tests.factories import ProductFactory
    cart, _ = Cart.objects.get_or_create(User=customer_user)
    product = ProductFactory(Stock=10, UnitPrice=150.00)
    Address.objects.create(user=product.Supplier.user, Street="S St", City="S City", State="Cairo")
    from orders.models import Warehouse
    warehouse_address = Address.objects.create(user=customer_user, Street="WH St", City="WH City", State="Cairo")
    Warehouse.objects.create(name="Cairo", Address=warehouse_address, delivery_fee=50.0)
    CartItems.objects.create(CartID=cart, Product=product, Quantity=1)
    
    url = reverse('payment:order-payment-process-order-payment')
    data = {
        "address_id": dummy_address.id
    }
    
    response = customer_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_200_OK, response.data
    assert response.data['url'] == "https://checkout.stripe.com/pay/cs_test_123"
    
    # Verify Stripe was called
    mock_create.assert_called_once()
