import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Handcrafts.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("SELECT data_type FROM information_schema.columns WHERE table_name = 'notifications_notification' AND column_name = 'object_id';")
    print("Database column type for object_id:", cursor.fetchone())
