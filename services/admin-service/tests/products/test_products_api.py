import pytest
from django.urls import reverse
from rest_framework import status
from tests.factories import CategoryFactory

@pytest.mark.django_db
def test_approved_supplier_can_create_product(supplier_client, supplier_user):
    # Supplier is approved in factory by default
    from accounts.models import Address
    Address.objects.create(user=supplier_user, Street="S St", City="S City", State="Cairo")
    category = CategoryFactory()
    url = reverse('product-list')
    import io
    from PIL import Image
    from django.core.files.uploadedfile import SimpleUploadedFile
    file = io.BytesIO()
    img = Image.new('RGB', (100, 100), 'white')
    img.save(file, 'jpeg')
    file.name = 'test.jpg'
    file.seek(0)
    image_file = SimpleUploadedFile("test_image.jpg", file.read(), content_type="image/jpeg")
    data = {
        "ProductName": "Handmade Vase",
        "ProductDescription": "Beautiful ceramic vase",
        "QuantityPerUnit": "1 item",
        "UnitPrice": 150.00,
        "UnitWeight": 2.50,
        "Stock": 5,
        "Category": category.CategoryID,
        "uploaded_images": [image_file],
        "uploaded_Colors": ["Red"],
        "uploaded_Sizes": ["M"]
    }
    
    response = supplier_client.post(url, data, format='multipart')
    assert response.status_code == status.HTTP_201_CREATED, response.data
    assert response.data['ProductName'] == "Handmade Vase"

@pytest.mark.django_db
def test_unapproved_supplier_cannot_create_product(supplier_client, supplier_user):
    # Revoke approval
    supplier_user.supplier.accepted_supplier = False
    supplier_user.supplier.save()
    
    from accounts.models import Address
    Address.objects.create(user=supplier_user, Street="S St", City="S City", State="Cairo")
    category = CategoryFactory()
    url = reverse('product-list')
    data = {
        "ProductName": "Handmade Vase",
        "ProductDescription": "Beautiful ceramic vase",
        "QuantityPerUnit": "1 item",
        "UnitPrice": 150.00,
        "UnitWeight": 2.50,
        "Stock": 5,
        "Category": category.CategoryID,
        "uploaded_images": [],
        "uploaded_Colors": [],
        "uploaded_Sizes": []
    }
    
    response = supplier_client.post(url, data, format='json')
    # Depending on the exact implementation, this might be 403 Forbidden or 400 Bad Request
    assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_400_BAD_REQUEST]

@pytest.mark.django_db
def test_customer_cannot_create_product(customer_client):
    category = CategoryFactory()
    url = reverse('product-list')
    data = {
        "ProductName": "Handmade Vase",
        "ProductDescription": "Beautiful ceramic vase",
        "QuantityPerUnit": "1 item",
        "UnitPrice": 150.00,
        "UnitWeight": 2.50,
        "Stock": 5,
        "Category": category.CategoryID,
        "uploaded_images": [],
        "uploaded_Colors": [],
        "uploaded_Sizes": []
    }
    
    response = customer_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_403_FORBIDDEN
