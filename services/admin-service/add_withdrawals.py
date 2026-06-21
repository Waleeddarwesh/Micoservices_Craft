import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Handcrafts.settings')
django.setup()

from returnrequest.models import BalanceWithdrawRequest
from accounts.models import User

# Try to find a user, fallback to the first active user
user = User.objects.filter(email='supplier1@craft.com').first()
if not user:
    user = User.objects.filter(is_active=True).first()

if not user:
    print("No users found to attach withdrawals to.")
    exit()

withdrawals = [
    {
        'amount': 500.00,
        'transfer_type': BalanceWithdrawRequest.TransferType.INSTAPAY,
        'transfer_number': 'supplier1_instapay',
        'transfer_status': BalanceWithdrawRequest.TransferStatus.REQUESTED,
        'notes': 'Need funds for inventory.'
    },
    {
        'amount': 1200.50,
        'transfer_type': BalanceWithdrawRequest.TransferType.BANK_TRANSFER,
        'transfer_number': 'EG12345678901234567890',
        'transfer_status': BalanceWithdrawRequest.TransferStatus.AWAITING_APPROVAL,
        'notes': 'Monthly payout'
    },
    {
        'amount': 250.00,
        'transfer_type': BalanceWithdrawRequest.TransferType.PHONE_WALLET,
        'transfer_number': '01012345678',
        'transfer_status': BalanceWithdrawRequest.TransferStatus.PROCESSING,
        'notes': 'Urgent withdrawal'
    }
]

for w in withdrawals:
    obj = BalanceWithdrawRequest.objects.create(
        user=user,
        amount=w['amount'],
        transfer_type=w['transfer_type'],
        transfer_number=w['transfer_number'],
        transfer_status=w['transfer_status'],
        notes=w['notes']
    )
    print(f"Created withdrawal request: {obj.id} for {w['amount']}")

print("Successfully added withdrawal requests.")
