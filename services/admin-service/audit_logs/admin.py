from django.contrib import admin
from .models import AuditLog

import json
from datetime import timedelta
from django.utils import timezone
from django.db.models import Count
from django.utils.html import format_html

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'formatted_user', 'formatted_action', 'entity_type', 'entity_id', 'ip_address')
    list_filter = ('action', 'entity_type', 'timestamp')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'action', 'entity_id', 'ip_address')
    readonly_fields = ('user', 'action', 'entity_type', 'entity_id', 'old_value', 'new_value', 'ip_address', 'user_agent', 'timestamp')
    
    def formatted_action(self, obj):
        action_lower = obj.action.lower()
        if 'create' in action_lower or 'add' in action_lower or 'register' in action_lower:
            color = '#28a745'
            bg = 'rgba(40, 167, 69, 0.1)'
        elif 'delete' in action_lower or 'remove' in action_lower:
            color = '#dc3545'
            bg = 'rgba(220, 53, 69, 0.1)'
        elif 'login' in action_lower or 'auth' in action_lower:
            color = '#17a2b8'
            bg = 'rgba(23, 162, 184, 0.1)'
        else:
            color = '#ffc107'
            bg = 'rgba(255, 193, 7, 0.1)'
            
        return format_html(
            '<span style="padding:4px 8px; border-radius:12px; font-size:12px; font-weight:600; color:{}; background-color:{}; white-space:nowrap;">{}</span>',
            color, bg, obj.action
        )
    formatted_action.short_description = "Action"
    
    def formatted_user(self, obj):
        if obj.user:
            return format_html(
                '<div style="display:flex; align-items:center; gap:8px;">'
                '<div style="width:24px; height:24px; border-radius:50%; background:#7fb04f; color:#fff; display:flex; align-items:center; justify-content:center; font-size:12px; font-weight:bold;">{}</div>'
                '<span>{}</span>'
                '</div>',
                obj.user.email[0].upper(), obj.user.email
            )
        return format_html('<span style="color:#888;"><i>System/Anonymous</i></span>')
    formatted_user.short_description = "Actor"

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        
        # Calculate statistics
        total_logs = AuditLog.objects.count()
        today_logs = AuditLog.objects.filter(timestamp__gte=timezone.now().replace(hour=0, minute=0, second=0)).count()
        unique_actors = AuditLog.objects.exclude(user=None).values('user').distinct().count()
        
        # Actions distribution for pie chart (top 5)
        actions_dist = AuditLog.objects.values('action').annotate(count=Count('id')).order_by('-count')[:5]
        action_labels = [item['action'] for item in actions_dist]
        action_data = [item['count'] for item in actions_dist]
        
        # Activity over last 7 days for line chart
        seven_days_ago = timezone.now() - timedelta(days=6)
        daily_activity = (
            AuditLog.objects.filter(timestamp__gte=seven_days_ago.replace(hour=0, minute=0, second=0))
            .extra(select={'day': 'date(timestamp)'})
            .values('day')
            .annotate(count=Count('id'))
            .order_by('day')
        )
        
        # Map daily_activity to an array of 7 days
        days = [(seven_days_ago + timedelta(days=i)).date() for i in range(7)]
        activity_dict = {str(item['day']): item['count'] for item in daily_activity}
        
        activity_labels = [day.strftime('%b %d') for day in days]
        activity_data = [activity_dict.get(str(day), 0) for day in days]

        extra_context.update({
            'total_logs': total_logs,
            'today_logs': today_logs,
            'unique_actors': unique_actors,
            'action_labels': json.dumps(action_labels),
            'action_data': json.dumps(action_data),
            'activity_labels': json.dumps(activity_labels),
            'activity_data': json.dumps(activity_data),
        })
        
        return super().changelist_view(request, extra_context=extra_context)

    def has_add_permission(self, request):
        return False
        
    def has_change_permission(self, request, obj=None):
        return False
        
    def has_delete_permission(self, request, obj=None):
        return False
