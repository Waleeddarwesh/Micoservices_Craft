import pytest
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import Permission

@pytest.mark.django_db
def test_anonymous_user_cannot_access_dashboard(api_client):
    url = reverse('admin-stats')
    response = api_client.get(url)
    assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

@pytest.mark.django_db
def test_customer_cannot_access_dashboard(customer_client):
    url = reverse('admin-stats')
    response = customer_client.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.django_db
def test_staff_without_permissions_can_access_identity_but_not_reports(staff_user_without_permission, api_client):
    api_client.force_authenticate(user=staff_user_without_permission)
    
    # Identity is open to any authenticated user to check their own role
    identity_url = reverse('admin-identity')
    identity_response = api_client.get(identity_url)
    assert identity_response.status_code == status.HTTP_200_OK
    assert identity_response.data['user']['is_staff'] is True

    # Reports require 'can_view_financial_reports'
    reports_url = reverse('admin-reports')
    reports_response = api_client.get(reports_url)
    assert reports_response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.django_db
def test_staff_with_permission_can_access_reports(staff_user_without_permission, api_client):
    perm = Permission.objects.get(codename='can_view_financial_reports')
    staff_user_without_permission.user_permissions.add(perm)
    
    api_client.force_authenticate(user=staff_user_without_permission)
    
    reports_url = reverse('admin-reports')
    reports_response = api_client.get(reports_url)
    assert reports_response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
def test_admin_can_access_everything(admin_client):
    url = reverse('admin-stats')
    response = admin_client.get(url)
    assert response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
def test_staff_cannot_suspend_users_without_permission(staff_user_without_permission, api_client, customer_user):
    api_client.force_authenticate(user=staff_user_without_permission)
    url = reverse('admin-user-toggle', kwargs={'pk': customer_user.pk})
    response = api_client.patch(url, {"is_active": False}, format='json')
    assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.django_db
def test_supplier_cannot_access_admin_dashboard(supplier_client):
    url = reverse('admin-stats')
    response = supplier_client.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.django_db
def test_anonymous_user_cannot_access_support_tickets(api_client):
    url = reverse('admin-support-tickets')
    response = api_client.get(url)
    assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

@pytest.mark.django_db
def test_staff_can_suspend_users_with_permission(staff_user_without_permission, api_client, customer_user):
    perm = Permission.objects.get(codename='can_suspend_users')
    staff_user_without_permission.user_permissions.add(perm)
    
    api_client.force_authenticate(user=staff_user_without_permission)
    url = reverse('admin-user-toggle', kwargs={'pk': customer_user.pk})
    response = api_client.patch(url, {"is_active": False}, format='json')
    assert response.status_code == status.HTTP_200_OK
    
    customer_user.refresh_from_db()
    assert customer_user.is_active is False
