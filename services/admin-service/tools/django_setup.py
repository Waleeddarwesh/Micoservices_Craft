import os
import django

def setup_django():
    """Initializes Django context. Must be called before any model imports."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Handcrafts.settings")
    try:
        from django.apps import apps
        if not apps.ready:
            django.setup()
    except Exception:
        django.setup()
