from django.core.management.base import BaseCommand
from developer_portal.models import APIService

SERVICES = [
    {
        "name": "Catalog & Video Service",
        "slug": "catalog-video",
        "version": "v2.0",
        "status": "healthy",
        "description": "Products, courses, videos, and catalog management APIs.",
        "schema_url": "/product/api/schema/?v=2",
        "endpoint_count": 42
    },
    {
        "name": "Orders Service",
        "slug": "orders",
        "version": "v2.0",
        "status": "healthy",
        "description": "Manage customer orders, shopping carts, and returns.",
        "schema_url": "/orders/api/schema/?v=2",
        "endpoint_count": 28
    },
    {
        "name": "Payments Service",
        "slug": "payments",
        "version": "v2.0",
        "status": "healthy",
        "description": "Process payments, refunds, and financial transactions.",
        "schema_url": "/payment/api/schema/?v=2",
        "endpoint_count": 15
    },
    {
        "name": "Platform Service",
        "slug": "platform",
        "version": "v2.0",
        "status": "healthy",
        "description": "Platform-wide features like reviews, disputes, and settings.",
        "schema_url": "/review/api/schema/?v=2",
        "endpoint_count": 31
    },
    {
        "name": "Reporting Service",
        "slug": "reporting",
        "version": "v2.0",
        "status": "healthy",
        "description": "Analytics, charts, and audit logs.",
        "schema_url": "/reports/api/schema/?v=2",
        "endpoint_count": 12
    },
    {
        "name": "Auth Service",
        "slug": "auth",
        "version": "v2.0",
        "status": "healthy",
        "description": "User authentication, JWT generation, and OAuth integration.",
        "schema_url": "/accounts/api/schema/?v=2",
        "endpoint_count": 18
    },
    {
        "name": "Admin API",
        "slug": "admin",
        "version": "v2.0",
        "status": "healthy",
        "description": "Central management API for the Craft Dashboard.",
        "schema_url": "/admin-schema.json?format=openapi&v=2",
        "endpoint_count": 56
    },
    {
        "name": "ML Recommendations",
        "slug": "ml",
        "version": "v1.0",
        "status": "healthy",
        "description": "AI-driven product and course recommendations (FastAPI).",
        "schema_url": "/recommendations/openapi.json",
        "endpoint_count": 5
    }
]

class Command(BaseCommand):
    help = 'Seeds the database with APIService data'

    def handle(self, *args, **kwargs):
        for s in SERVICES:
            APIService.objects.update_or_create(
                slug=s['slug'],
                defaults={
                    'name': s['name'],
                    'version': s['version'],
                    'status': s['status'],
                    'description': s['description'],
                    'schema_url': s['schema_url'],
                    'endpoint_count': s['endpoint_count'],
                    'is_active': True,
                }
            )
        self.stdout.write(self.style.SUCCESS('Successfully seeded APIServices'))
