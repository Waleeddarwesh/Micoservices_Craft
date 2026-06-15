import pytest
from rest_framework.test import APIClient
from tests.factories import UserFactory, CustomerFactory, SupplierFactory, GroupFactory
from accounts.models import Address

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def customer_user():
    customer = CustomerFactory()
    return customer.user

@pytest.fixture
def customer_client(api_client, customer_user):
    api_client.force_authenticate(user=customer_user)
    return api_client

@pytest.fixture
def supplier_user():
    supplier = SupplierFactory()
    return supplier.user

@pytest.fixture
def supplier_client(api_client, supplier_user):
    api_client.force_authenticate(user=supplier_user)
    return api_client

@pytest.fixture
def admin_user():
    return UserFactory(is_staff=True, is_superuser=True)

@pytest.fixture
def admin_client(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    return api_client

@pytest.fixture
def operations_group():
    return GroupFactory(name="Operations")

@pytest.fixture
def support_group():
    return GroupFactory(name="Support")

@pytest.fixture
def sales_group():
    return GroupFactory(name="Sales")

@pytest.fixture
def staff_user_without_permission():
    return UserFactory(is_staff=True)

@pytest.fixture
def staff_user_with_permission(support_group):
    user = UserFactory(is_staff=True)
    user.groups.add(support_group)
    return user

@pytest.fixture
def dummy_address(customer_user):
    return Address.objects.create(
        user=customer_user,
        Street="123 Test St",
        City="Cairo",
        State="Cairo"
    )
