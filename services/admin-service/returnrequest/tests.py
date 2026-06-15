from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from accounts.models import User, Supplier
from returnrequest.models import ReturnRequest
from orders.models import Order
from products.models import Product

class ReturnRequestSecurityTests(APITestCase):
    def setUp(self):
        # Create Users
        self.supplier1_user = User.objects.create_user(
            email="supplier1@crafteg.com", password="Password123!", PhoneNO="01011111111", is_supplier=True, is_verified=True, first_name="A", last_name="B"
        )
        self.supplier1 = Supplier.objects.create(user=self.supplier1_user)
        
        self.supplier2_user = User.objects.create_user(
            email="supplier2@crafteg.com", password="Password123!", PhoneNO="01022222222", is_supplier=True, is_verified=True, first_name="C", last_name="D"
        )
        self.supplier2 = Supplier.objects.create(user=self.supplier2_user)
        
        self.customer_user = User.objects.create_user(
            email="customer@crafteg.com", password="Password123!", PhoneNO="01033333333", is_customer=True, is_verified=True, first_name="E", last_name="F"
        )

        # Create Products
        self.product1 = Product.objects.create(Supplier=self.supplier1, ProductName="Product 1", UnitPrice=100, UnitWeight=1.0, Stock=10)
        
        # Create Order
        from accounts.models import Address
        self.address = Address.objects.create(user=self.customer_user, Street="Main", City="Cairo", State="Cairo")
        self.order1 = Order.objects.create(user=self.customer_user, total_amount=100, address=self.address)
        
        # Create Return Request associated with Supplier 1
        self.return_request = ReturnRequest.objects.create(
            user=self.customer_user,
            order=self.order1,
            product=self.product1,
            quantity=1,
            supplier=self.supplier1,
            amount=100.0,
            reason="damaged"
        )
        
        self.login_url = reverse('login')

    def authenticate(self, user):
        res = self.client.post(self.login_url, {"email": user.email, "password": "Password123!"})
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + res.data['access'])

    def test_idor_prevented_on_approve(self):
        """Supplier 2 should not be able to approve Supplier 1's return request."""
        self.authenticate(self.supplier2_user)
        url = reverse('return-request-approve', kwargs={'pk': self.return_request.pk})
        response = self.client.post(url)
        # Should be 404 because get_queryset won't find it (or 403)
        self.assertIn(response.status_code, [status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN])

    def test_owner_can_approve(self):
        """Supplier 1 should be able to approve their own return request."""
        self.authenticate(self.supplier1_user)
        url = reverse('return-request-approve', kwargs={'pk': self.return_request.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
