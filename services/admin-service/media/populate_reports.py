import os
import sys
import django
import random
from datetime import timedelta
from decimal import Decimal

sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Handcrafts.settings')
django.setup()

from django.utils import timezone
from accounts.models import User, Address
from orders.models import Order
from returnrequest.models import Transaction

now = timezone.now()
users = list(User.objects.filter(is_active=True)[:5])
if not users:
    print("No users found")
    sys.exit(0)

address = Address.objects.first()
if not address:
    user = users[0]
    address = Address.objects.create(user=user, FullName="Test", PhoneNumber="123", Governorates="Cairo", City="Cairo", Street="Test")

# 1. Payment Methods (Orders)
payment_methods = ['Cash on Delivery', 'Credit Card', 'Balance']
for _ in range(30):
    user = random.choice(users)
    method = random.choice(payment_methods)
    amount = Decimal(random.randint(100, 1000))
    days_ago = random.randint(0, 30)
    created = now - timedelta(days=days_ago)
    
    order = Order.objects.create(
        user=user,
        address=address,
        payment_method=method,
        total_amount=amount,
        final_amount=amount,
        paid=True,
        status='delivered successfully'
    )
    Order.objects.filter(id=order.id).update(created_at=created)

# 2. Outcome (Transactions)
outcome_types = ['WITHDRAWAL_REQUEST', 'RETURN_DEBIT', 'REFUND_FAILED']
for _ in range(15):
    user = random.choice(users)
    ttype = random.choice(outcome_types)
    amount = Decimal(random.randint(50, 500))
    days_ago = random.randint(0, 30)
    created = now - timedelta(days=days_ago)
    
    txn = Transaction.objects.create(
        user=user,
        transaction_type=ttype,
        amount=amount
    )
    Transaction.objects.filter(id=txn.id).update(created_at=created)

print("Data generated successfully.")
