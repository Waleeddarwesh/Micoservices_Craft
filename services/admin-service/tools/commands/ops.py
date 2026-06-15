import os
import sys
import time
import secrets
import string

from tools.django_setup import setup_django
from tools.core.registry import register_command
from tools.core.safety import prevent_production, confirm_dangerous_action
from tools.core.output import print_info, print_success, print_error, print_warning

def generate_random_password(length=12):
    characters = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(characters) for i in range(length))

def _do_assign_group_permissions(args):
    from django.contrib.auth.models import Group, Permission
    print_info("Assigning permissions to groups...")
    GROUP_PERMISSIONS = {
        "Operations": [
            "can_manage_products",
            "can_manage_disputes",
            "can_suspend_users",
            "can_manage_support_tickets",
            "can_verify_suppliers",
            "can_manage_courses",
            "can_moderate_reviews",
        ],
        "Support": [
            "can_manage_support_tickets",
            "can_manage_disputes",
        ],
        "Sales": [
            "can_view_financial_reports",
            "can_approve_withdrawals",
            "can_refund_orders",
        ]
    }
    
    if args.dry_run:
        for group_name, perms in GROUP_PERMISSIONS.items():
            print_info(f"Would create/update group '{group_name}' and assign {len(perms)} permissions.")
        print_info("No database changes were applied.")
        return 0

    for group_name, perm_codenames in GROUP_PERMISSIONS.items():
        group, _ = Group.objects.get_or_create(name=group_name)
        perms = Permission.objects.filter(codename__in=perm_codenames)
        group.permissions.set(perms)
        print_success(f"Assigned {perms.count()} permissions to {group_name} group.")
    print_success("Permission assignment complete!")
    return 0

@register_command("assign-group-permissions")
def run_assign_group_permissions(args):
    exit_code = prevent_production("assign-group-permissions")
    if exit_code != 0: return exit_code
    
    setup_django()
    return _do_assign_group_permissions(args)

def _do_setup_ops_teams(args):
    from django.contrib.auth.models import Group
    from accounts.models import User
    
    TEST_PASSWORD = os.getenv("CRAFT_TEST_PASSWORD", "ChangeMe123!")
    teams = ["Operations", "Support", "Sales"]
    
    print_info("Setting up groups and test users...")
    
    if args.dry_run:
        for team in teams:
            print_info(f"Would create group: {team}")
            print_info(f"Would create user: {team.lower()}_tester@craft.com")
        print_info("No database changes were applied.")
        return 0

    for team_name in teams:
        group, created = Group.objects.get_or_create(name=team_name)
        if created:
            print_success(f"Created group: {team_name}")
        else:
            print_info(f"Group already exists: {team_name}")
            
        email = f"{team_name.lower()}_tester@craft.com"
        user, u_created = User.objects.get_or_create(
            email=email,
            defaults={
                "first_name": f"{team_name}",
                "last_name": "Tester",
                "is_staff": True,
                "is_verified": True
            }
        )
        
        user.set_password(TEST_PASSWORD)
        user.save()
        
        if u_created:
            print_success(f"Created user: {email} (Password set from env)")
        else:
            print_success(f"Updated existing user: {email} (Password updated)")
            
        user.groups.add(group)
        print_success(f"Added {email} to {team_name} group.")
    print_success("Operations teams setup complete!")
    return 0

@register_command("setup-ops-teams")
def run_setup_ops_teams(args):
    exit_code = prevent_production("setup-ops-teams")
    if exit_code != 0: return exit_code
    
    setup_django()
    return _do_setup_ops_teams(args)

@register_command("upgrade-user")
def run_upgrade_user(args):
    exit_code = prevent_production("upgrade-user")
    if exit_code != 0: return exit_code

    setup_django()
    from accounts.models import User
    
    TEST_PASSWORD = os.getenv("CRAFT_TEST_PASSWORD", "ChangeMe123!")
    
    if len(sys.argv) > 2:
        email = sys.argv[2]
    else:
        email = input("Enter email to upgrade: ")
        
    if args.dry_run:
        print_info(f"Would upgrade/create superuser: {email}")
        print_info("No database changes were applied.")
        return 0

    try:
        user = User.objects.get(email__iexact=email)
        user.is_staff = True
        user.is_superuser = True
        user.is_verified = True
        user.save()
        print_success(f"Successfully upgraded {email} to Superuser/Staff!")
    except User.DoesNotExist:
        user = User.objects.create_superuser(email=email, password=TEST_PASSWORD)
        user.is_verified = True
        user.save()
        print_success(f"Created new superuser {email}")
    return 0

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title):
    print("\n" + "="*50)
    print(f"  {title.upper()}")
    print("="*50 + "\n")

@register_command("ops-manager")
def run_ops_manager(args):
    # ops-manager is interactive, not suited for CI/CD, skip dry_run logic here
    setup_django()
    from tools.commands.ops_manager_utils import main_menu
    try:
        main_menu()
    except KeyboardInterrupt:
        print_info("Operation cancelled by user. Exiting.")
        return 1
    return 0
