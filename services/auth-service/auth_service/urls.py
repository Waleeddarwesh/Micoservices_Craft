from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('auth/', include('social_django.urls', namespace='social')),
    path('internal/', include('accounts.internal_urls')),
]
