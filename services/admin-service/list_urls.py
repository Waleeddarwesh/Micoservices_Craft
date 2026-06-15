import os
import django
from django.urls import get_resolver

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Handcrafts.settings')
django.setup()

def get_urls(url_patterns, prefix=''):
    urls = []
    for pattern in url_patterns:
        if hasattr(pattern, 'url_patterns'):
            urls.extend(get_urls(pattern.url_patterns, prefix + str(pattern.pattern)))
        else:
            urls.append(prefix + str(pattern.pattern))
    return urls

urls = get_urls(get_resolver().url_patterns)
for url in sorted(set(urls)):
    print(url)
