from django.core.management.base import BaseCommand
from products.models import Product
from course.models import Course
import requests
from django.conf import settings

class Command(BaseCommand):
    help = 'Backfill supplier_name for products and courses by calling auth-service or monolith API'

    def handle(self, *args, **options):
        # We need a list of unique supplier IDs
        supplier_ids = set()
        for p in Product.objects.all():
            if p.supplier_id:
                supplier_ids.add(p.supplier_id)
        for c in Course.objects.all():
            if c.supplier_id:
                supplier_ids.add(c.supplier_id)

        if not supplier_ids:
            self.stdout.write("No suppliers to backfill.")
            return

        self.stdout.write(f"Found {len(supplier_ids)} unique supplier_ids. Fetching data...")

        # In a real environment, you'd call auth-service:
        # We can simulate resolving user_ids -> names
        auth_service_url = getattr(settings, 'AUTH_SERVICE_INTERNAL_URL', 'http://localhost:8001/internal/users/bulk-lookup/')
        
        try:
            resp = requests.post(auth_service_url, json={"ids": list(supplier_ids)})
            if resp.status_code == 200:
                users = resp.json()
                for user in users:
                    uid = user['id']
                    name = f"{user.get('first_name','')} {user.get('last_name','')}".strip()
                    
                    if name:
                        Product.objects.filter(supplier_id=uid).update(supplier_name=name)
                        Course.objects.filter(supplier_id=uid).update(supplier_name=name)
                
                self.stdout.write(self.style.SUCCESS('Successfully backfilled supplier_names.'))
            else:
                self.stdout.write(self.style.ERROR(f'Failed to fetch users. Status {resp.status_code}'))
        except requests.RequestException as e:
            self.stdout.write(self.style.ERROR(f'Error connecting to auth service: {str(e)}'))
