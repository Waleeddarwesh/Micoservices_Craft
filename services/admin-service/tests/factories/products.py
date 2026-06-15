import factory
from factory.django import DjangoModelFactory
from products.models import Category, Product
from tests.factories.users import SupplierFactory

class CategoryFactory(DjangoModelFactory):
    class Meta:
        model = Category

    Title = factory.Sequence(lambda n: f"Category {n}")
    Description = factory.Faker('text')
    Active = True
    Slug = factory.Sequence(lambda n: f"category-{n}")

class ProductFactory(DjangoModelFactory):
    class Meta:
        model = Product

    ProductName = factory.Sequence(lambda n: f"Product {n}")
    ProductDescription = factory.Faker('text')
    Category = factory.SubFactory(CategoryFactory)
    Supplier = factory.SubFactory(SupplierFactory)
    QuantityPerUnit = "1 item"
    UnitPrice = __import__('decimal').Decimal("100.00")
    UnitWeight = __import__('decimal').Decimal("1.00")
    Stock = 10
    Publish_Date = factory.LazyFunction(lambda: __import__('django.utils.timezone').utils.timezone.now())
    publish_status = 'approved'
