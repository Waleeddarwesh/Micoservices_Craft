import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admin_service.settings')
django.setup()

from returnrequest.models import Transaction
from accounts.models import User

craft_user = User.objects.get(email="CraftEG@craft.com")
print("Craft Transactions:")
for t in Transaction.objects.filter(user=craft_user)[:20]:
    print(f"Type: {t.transaction_type}, Amount: {t.amount}, Date: {t.created_at}")

print("\nOther positive transactions (like SUPPLIER_TRANSFER):")
for t in Transaction.objects.filter(transaction_type='SUPPLIER_TRANSFER')[:5]:
    print(f"User: {t.user.email}, Amount: {t.amount}")

print("\nOther positive transactions (like PURCHASED_PRODUCTS):")
for t in Transaction.objects.filter(transaction_type='PURCHASED_PRODUCTS', amount__gt=0)[:5]:
    print(f"User: {t.user.email}, Amount: {t.amount}")
