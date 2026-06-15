import pytest
from django.urls import reverse
from rest_framework import status
from accounts.models import User

@pytest.mark.django_db
def test_customer_can_register(api_client):
    url = reverse('register_customer')
    data = {
        "email": "newcustomer@example.com",
        "first_name": "New",
        "last_name": "Customer",
        "password": "StrongPassword123!",
        "password2": "StrongPassword123!",
        "PhoneNO": "01000000000"
    }
    
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['email'] == "newcustomer@example.com"
    
    user = User.objects.get(email="newcustomer@example.com")
    assert user.is_customer is True
    assert user.is_verified is False # Pending OTP

@pytest.mark.django_db
def test_customer_can_login(api_client, customer_user):
    # customer_user fixture already sets password to 'Password123!'
    url = reverse('login')
    data = {
        "email": customer_user.email,
        "password": "Password123!"
    }
    
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert 'access' in response.data
    assert 'refresh' in response.data

@pytest.mark.django_db
def test_customer_profile_access(customer_client):
    url = reverse('customer-profile')
    response = customer_client.get(url)
    assert response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
def test_unauthenticated_user_cannot_access_profile(api_client):
    url = reverse('customer-profile')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
