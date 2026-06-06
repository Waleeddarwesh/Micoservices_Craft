from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

# A map of roles to their permissions
ROLES = {
    'Super Admin': [
        'can_approve_withdrawals', 'can_refund_orders', 'can_suspend_users',
        'can_verify_suppliers', 'can_manage_courses', 'can_manage_products',
        'can_manage_disputes', 'can_view_financial_reports', 'can_view_audit_logs',
        'can_manage_support_tickets'
    ],
    'Admin': [
        'can_approve_withdrawals', 'can_refund_orders', 'can_suspend_users',
        'can_verify_suppliers', 'can_manage_disputes', 'can_view_audit_logs',
        'can_manage_support_tickets'
    ],
    'Finance Manager': [
        'can_approve_withdrawals', 'can_refund_orders', 'can_view_financial_reports'
    ],
    'Content Manager': [
        'can_manage_courses', 'can_manage_products'
    ],
    'Support Agent': [
        'can_manage_support_tickets', 'can_manage_disputes', 'can_refund_orders'
    ],
    'Supplier': [],
    'Customer': [],
    'Delivery Agent': [],
}

class Command(BaseCommand):
    help = 'Create default roles (Groups) and assign permissions'

    def handle(self, *args, **options):
        # We assume custom permissions are attached to the User model as defined in accounts.models.User
        from accounts.models import User
        user_ct = ContentType.objects.get_for_model(User)

        for role_name, perms in ROLES.items():
            group, created = Group.objects.get_or_create(name=role_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created group: {role_name}'))
            
            # Assign permissions
            for codename in perms:
                try:
                    perm = Permission.objects.get(codename=codename, content_type=user_ct)
                    group.permissions.add(perm)
                except Permission.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f'Permission {codename} not found! Run makemigrations/migrate first.'))
            
            self.stdout.write(self.style.SUCCESS(f'Successfully assigned permissions to {role_name}'))
            
        self.stdout.write(self.style.SUCCESS('Roles and permissions setup complete.'))
