from django.contrib import admin
from .models import DeveloperAPIKey, WebhookEndpoint, WebhookDelivery, ChangelogEntry, APIService

@admin.register(APIService)
class APIServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'version', 'status', 'is_active')
    list_filter = ('status', 'is_active')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(DeveloperAPIKey)
class DeveloperAPIKeyAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'environment', 'key_prefix', 'is_active', 'created_at')
    list_filter = ('environment', 'is_active')
    search_fields = ('name', 'owner__email', 'key_prefix')
    readonly_fields = ('hashed_key',)

@admin.register(WebhookEndpoint)
class WebhookEndpointAdmin(admin.ModelAdmin):
    list_display = ('url', 'owner', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('url', 'owner__email')

@admin.register(WebhookDelivery)
class WebhookDeliveryAdmin(admin.ModelAdmin):
    list_display = ('endpoint', 'event', 'status_code', 'success', 'created_at')
    list_filter = ('success', 'event')
    search_fields = ('endpoint__url',)

@admin.register(ChangelogEntry)
class ChangelogEntryAdmin(admin.ModelAdmin):
    list_display = ('title', 'version', 'entry_type', 'published_date')
    list_filter = ('entry_type',)
    search_fields = ('title', 'description')
