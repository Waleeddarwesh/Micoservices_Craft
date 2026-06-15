import factory
from factory.django import DjangoModelFactory
from django.contrib.auth.models import Group
from django.utils import timezone
from accounts.models import User, Customer, Supplier

class GroupFactory(DjangoModelFactory):
    class Meta:
        model = Group
        django_get_or_create = ('name',)

    name = factory.Sequence(lambda n: f"Group {n}")

class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ('email',)

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    PhoneNO = factory.Sequence(lambda n: f"010{n:08d}")
    password = factory.PostGenerationMethodCall('set_password', 'Password123!')
    is_active = True
    is_verified = True
    date_joined = factory.LazyFunction(timezone.now)

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        raw_password = extracted or "Password123!"
        self.set_password(raw_password)
        if create:
            self.save()

class CustomerFactory(DjangoModelFactory):
    class Meta:
        model = Customer

    user = factory.SubFactory(UserFactory, is_customer=True)

class SupplierFactory(DjangoModelFactory):
    class Meta:
        model = Supplier

    user = factory.SubFactory(UserFactory, is_supplier=True)
    CategoryTitle = "Handcrafts"
    ExperienceYears = 5
    accepted_supplier = True
    SupplierContract = "contract.pdf"
    SupplierIdentity = "identity.pdf"
