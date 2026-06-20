from rest_framework.permissions import BasePermission


class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        # For StatelessUser from JWT, check roles in payload
        payload = getattr(request.user, 'payload', None)
        if payload:
            return 'customer' in payload.get('roles', [])
        # Fallback for real Django User (e.g., in auth-service)
        return hasattr(request.user, 'customer')


class IsSupplier(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        # For StatelessUser from JWT, check roles in payload
        payload = getattr(request.user, 'payload', None)
        if payload:
            return 'supplier' in payload.get('roles', [])
        # Fallback for real Django User
        return hasattr(request.user, 'supplier')

    def has_object_permission(self, request, view, obj):
        # Check if the user is the supplier/owner of the course
        user_id = getattr(request.user, 'id', None)
        if hasattr(obj, 'supplier_id'):
            return obj.supplier_id == int(user_id) if user_id else False
        return False


class IsSupplierOrCustomer(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        payload = getattr(request.user, 'payload', None)
        if payload:
            roles = payload.get('roles', [])
            return 'supplier' in roles or 'customer' in roles
        return hasattr(request.user, 'supplier') or hasattr(request.user, 'customer')
