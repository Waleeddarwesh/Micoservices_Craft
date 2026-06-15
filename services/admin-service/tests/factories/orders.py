import factory
from factory.django import DjangoModelFactory
from orders.models import Cart, CartItems, Order, OrderItem
from tests.factories.users import UserFactory
from tests.factories.products import ProductFactory

class CartFactory(DjangoModelFactory):
    class Meta:
        model = Cart

    User = factory.SubFactory(UserFactory)

class CartItemFactory(DjangoModelFactory):
    class Meta:
        model = CartItems

    CartID = factory.SubFactory(CartFactory)
    Product = factory.SubFactory(ProductFactory)
    Quantity = 1

class OrderFactory(DjangoModelFactory):
    class Meta:
        model = Order

    user = factory.SubFactory(UserFactory)
    total_amount = 100.00
    # Address is required, so we should either create an AddressFactory or set it later.
    # Since we need it, let's just make it required in the test or create a default.
    # We will pass address explicitly when creating an order.

class OrderItemFactory(DjangoModelFactory):
    class Meta:
        model = OrderItem

    order = factory.SubFactory(OrderFactory)
    product = factory.SubFactory(ProductFactory)
    quantity = 1
    price = 100.00
