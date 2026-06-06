"""
accounts/management/commands/seed_demo_data.py — Auth Service
Address seed logic removed: Address has been extracted to the order-service.
Auth-service only seeds user accounts and roles.

To seed addresses, run the corresponding command in order-service:
  python manage.py seed_demo_addresses
"""
import logging

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()

logger = logging.getLogger(__name__)

DEMO_USERS = [
    {
        "email":      "admin@craft.dev",
        "username":   "admin",
        "first_name": "Admin",
        "last_name":  "User",
        "role":       "admin",
        "password":   "admin1234!",
    },
    {
        "email":      "supplier@craft.dev",
        "username":   "supplier1",
        "first_name": "Demo",
        "last_name":  "Supplier",
        "role":       "supplier",
        "password":   "supplier1234!",
    },
    {
        "email":      "customer@craft.dev",
        "username":   "customer1",
        "first_name": "Demo",
        "last_name":  "Customer",
        "role":       "customer",
        "password":   "customer1234!",
    },
    {
        "email":      "delivery@craft.dev",
        "username":   "delivery1",
        "first_name": "Demo",
        "last_name":  "Driver",
        "role":       "delivery",
        "password":   "delivery1234!",
    },
]


class Command(BaseCommand):
    help = (
        "Seed demo user accounts for local development. "
        "Address data is owned by order-service — run seed_demo_addresses there."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete existing demo users before seeding.",
        )

    def handle(self, *args, **options):
        if options["reset"]:
            demo_emails = [u["email"] for u in DEMO_USERS]
            deleted, _ = User.objects.filter(email__in=demo_emails).delete()
            self.stdout.write(self.style.WARNING(f"Deleted {deleted} existing demo users."))

        created_count = 0
        for data in DEMO_USERS:
            user, created = User.objects.get_or_create(
                email=data["email"],
                defaults={
                    "username":   data["username"],
                    "first_name": data["first_name"],
                    "last_name":  data["last_name"],
                    "role":       data["role"],
                    "is_active":  True,
                },
            )
            if created:
                user.set_password(data["password"])
                user.save()
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"  Created {data['role']}: {data['email']}")
                )
            else:
                self.stdout.write(f"  Skipped (already exists): {data['email']}")

        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone. {created_count}/{len(DEMO_USERS)} demo users created.\n"
                "NOTE: Address seeding is handled by order-service "
                "(`python manage.py seed_demo_addresses`)."
            )
        )
