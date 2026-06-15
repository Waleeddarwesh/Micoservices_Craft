from django.utils import translation

def activate_language(language_code):
    """Activate a language for the current thread."""
    translation.activate(language_code or 'en')
