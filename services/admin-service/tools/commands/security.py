import os
import re

from tools.core.registry import register_command
from tools.core.output import print_info, print_success, print_error, print_warning

def is_allowlisted(line: str) -> bool:
    allowlist = [
        "os.getenv",
        "os.environ.get",
        "config(",
        "env(",
        "getenv(",
        "test-secret-key-for-ci",
        "sk_test_dummy",
        "TestPass123",
        "Password123",
        "craftpassword123",
        "${{ secrets.",
    ]
    return any(item in line for item in allowlist)

@register_command("scan-secrets")
def run_scan_secrets(args):
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    
    SECRET_PATTERNS = [
        r'SECRET_KEY\s*=\s*["\'][^"\']{20,}["\']',
        r'password\s*=\s*["\'][^"\']{8,}["\']',
        r'token\s*=\s*["\'][^"\']{20,}["\']',
        r'api[_-]?key\s*=\s*["\'][^"\']{20,}["\']',
        r'sk_live_[A-Za-z0-9_]+',
        r'AKIA[0-9A-Z]{16}',
    ]

    ignored_dirs = {".git", ".venv", "venv", "__pycache__", "node_modules", ".pytest_cache", "htmlcov"}

    real_findings = []
    warning_findings = []
    
    if args.dry_run:
        print_info("Would scan the entire project directory for secrets.")
        return 0

    for root, dirs, files in os.walk(base_dir):
        dirs[:] = [d for d in dirs if d not in ignored_dirs]

        for file in files:
            if file == ".coverage":
                continue
            if file.endswith((".py", ".env", ".yml", ".yaml", ".json", ".md")):
                path = os.path.join(root, file)
                try:
                    with open(path, encoding="utf-8", errors="ignore") as f:
                        lines = f.readlines()
                except Exception:
                    continue

                for line in lines:
                    for pattern in SECRET_PATTERNS:
                        if re.search(pattern, line, re.IGNORECASE):
                            if is_allowlisted(line):
                                warning_findings.append((path, line.strip(), pattern))
                            else:
                                real_findings.append((path, line.strip(), pattern))

    if warning_findings:
        print_warning("Possible false-positive secrets found:")
        for path, line, pattern in warning_findings:
            print_warning(f"  - {path} matched {pattern}")

    if real_findings:
        print_error("Possible real secrets found:")
        for path, line, pattern in real_findings:
            print_error(f"  - {path} matched {pattern}")
        return 1

    print_success("No obvious secrets found.")
    return 0

@register_command("audit-permissions")
def run_audit_permissions(args):
    from tools.django_setup import setup_django
    setup_django()

    from django.contrib.auth.models import Group
    from accounts.models import User
    
    if args.dry_run:
        print_info("Would audit group counts and permissions, and query staff users without groups.")
        return 0

    print_info("Groups:")
    for group in Group.objects.all():
        print_info(f"- {group.name}: {group.permissions.count()} permissions, {group.user_set.count()} users")

    print_info("\nStaff users without groups:")
    users = User.objects.filter(is_staff=True, groups__isnull=True)

    for user in users:
        print_warning(f"- {user.email}")

    if not users.exists():
        print_success("No staff users without groups.")
    else:
        return 1
        
    return 0

@register_command("check-superusers")
def run_check_superusers(args):
    from tools.django_setup import setup_django
    setup_django()
    from accounts.models import User
    
    if args.dry_run:
        print_info("Would query all superusers.")
        return 0
        
    superusers = User.objects.filter(is_superuser=True)
    count = superusers.count()
    print_info(f"Found {count} superusers:")
    for su in superusers:
        print_warning(f"  - {su.email}")
        
    if count > 2:
        print_warning("More than 2 superusers found! Check if this is intended.")
        
    return 0

@register_command("check-staff-users")
def run_check_staff_users(args):
    from tools.django_setup import setup_django
    setup_django()
    from accounts.models import User
    
    if args.dry_run:
        print_info("Would query all staff users.")
        return 0
        
    staff = User.objects.filter(is_staff=True)
    count = staff.count()
    print_info(f"Found {count} staff users.")
    for st in staff:
        groups = ", ".join([g.name for g in st.groups.all()])
        print_info(f"  - {st.email} (Groups: {groups or 'None'})")
        
    return 0
