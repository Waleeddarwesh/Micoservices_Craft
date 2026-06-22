import json
from .models import AuditLog

class SystemAdminAuditMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Log only actions affecting system_admin paths
        if request.path.startswith('/api/system-admin/') and request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            user = request.user if request.user.is_authenticated else None
            ip_address = request.META.get('REMOTE_ADDR')
            action = request.method
            resource = request.path
            
            # Optionally capture details (be careful not to log sensitive data or huge bodies)
            details = {}
            if response.status_code >= 400:
                details['error_code'] = response.status_code
                
            AuditLog.objects.create(
                user=user,
                action=action,
                resource=resource,
                details=details,
                ip_address=ip_address
            )

        return response
