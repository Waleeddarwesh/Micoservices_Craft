import os
import sys

from tools.core.registry import register_command, get_command
from tools.core.output import print_info, print_success, print_error, print_warning

@register_command("check-env")
def run_check_env(args):
    required = [
        "SECRET_KEY",
        "DATABASE_URL",
        "REDIS_URL",
        "EMAIL_HOST",
        "EMAIL_HOST_USER",
        "EMAIL_HOST_PASSWORD",
        "STRIPE_SECRET_KEY",
    ]

    missing = []
    for key in required:
        if not os.getenv(key):
            missing.append(key)

    if missing:
        print_error("Missing environment variables:")
        for key in missing:
            print_error(f"  - {key}")
        return 1
    else:
        print_success("All required environment variables exist.")
        return 0

@register_command("check-services")
def run_check_services(args):
    from tools.django_setup import setup_django
    setup_django()

    from django.core.cache import cache
    from django.db import connection

    print_info("Checking database...")
    errors = 0
    try:
        connection.ensure_connection()
        print_success("Database OK")
    except Exception as e:
        print_error(f"Database failed: {e}")
        errors += 1

    print_info("Checking cache / Redis...")
    try:
        cache.set("health_check", "ok", timeout=10)
        value = cache.get("health_check")
        if value == "ok":
            print_success("Cache / Redis OK")
        else:
            print_error("Cache returned wrong value")
            errors += 1
    except Exception as e:
        print_error(f"Cache / Redis failed: {e}")
        errors += 1
        
    return 1 if errors > 0 else 0

@register_command("docker-check")
def run_docker_check(args):
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

    dockerfile = os.path.join(base_dir, "Dockerfile")
    dockerignore = os.path.join(base_dir, ".dockerignore")
    requirements = os.path.join(base_dir, "requirements.txt")

    checks = [
        ("Dockerfile exists", os.path.exists(dockerfile)),
        (".dockerignore exists", os.path.exists(dockerignore)),
        ("requirements.txt exists", os.path.exists(requirements)),
    ]

    errors = 0
    for name, passed in checks:
        if passed:
            print_success(name)
        else:
            print_error(name)
            errors += 1

    if os.path.exists(dockerignore):
        try:
            with open(dockerignore, encoding="utf-8", errors="ignore") as f:
                content = f.read()
            important_ignores = [".env", "db.sqlite3", "__pycache__", ".git", "media"]

            for item in important_ignores:
                if item in content:
                    print_success(f"{item} is ignored")
                else:
                    print_warning(f"{item} is not ignored")
        except Exception as e:
            print_error(f"Could not read .dockerignore: {e}")
            errors += 1
            
    return 1 if errors > 0 else 0

@register_command("quick-deploy-check")
def run_quick_deploy_check(args):
    import subprocess
    print_info("Running Django deployment checks...")
    try:
        result = subprocess.run([sys.executable, "manage.py", "check", "--deploy"], check=False)
        if result.returncode == 0:
            print_success("Deployment check passed.")
            return 0
        else:
            print_error("Deployment check found issues.")
            return 1
    except Exception as e:
        print_error(f"Deployment check failed to run: {e}")
        return 1

@register_command("check-health")
def run_check_health(args):
    print_info("Running quick health check...")
    from tools.django_setup import setup_django
    try:
        setup_django()
        from django.db import connection
        connection.ensure_connection()
        print_success("Database connection OK.")
        return 0
    except Exception as e:
        print_error(f"Health check failed: {e}")
        return 1

@register_command("pre-deploy")
def run_pre_deploy(args):
    print_info("=" * 40)
    print_info("RUNNING PRE-DEPLOYMENT READINESS CHECKS")
    print_info("=" * 40)
    
    commands = [
        "check-env",
        "check-health",
        "check-services",
        "check-migrations",
        "check-static",
        "quick-deploy-check",
        "scan-secrets",
        "docker-check"
    ]
    
    for cmd in commands:
        print_info(f"\n---> {cmd.upper()}")
        func = get_command(cmd)
        if func:
            exit_code = func(args)
            if exit_code != 0:
                print_error(f"Pre-deploy failed at step: {cmd}")
                return exit_code
    
    print_success("\nAll pre-deployment checks passed successfully!")
    return 0

@register_command("version")
def run_version(args):
    import django
    from django.conf import settings
    from tools.django_setup import setup_django
    from tools.core.safety import is_production
    
    setup_django()
    
    env_name = "production" if is_production() else "development"
    if not is_production() and os.getenv("DEBUG", "").lower() in {"false", "0"}:
        env_name = "staging (DEBUG=False)"
        
    print_info("Craft CLI v1.0.0")
    print_info(f"Django settings: {os.environ.get('DJANGO_SETTINGS_MODULE', 'Handcrafts.settings')}")
    print_info(f"Environment: {env_name}")
    print_info(f"Python: {sys.version.split(' ')[0]}")
    print_info(f"Django: {django.get_version()}")
    return 0

@register_command("doctor")
def run_doctor(args):
    print_info("=" * 40)
    print_info("RUNNING PROJECT DOCTOR")
    print_info("=" * 40)
    
    commands = [
        "check-env",
        "check-health",
        "check-services",
        "check-migrations",
        "docker-check",
        "quick-deploy-check",
        "scan-secrets",
        "audit-permissions"
    ]
    
    results = {}
    
    for cmd in commands:
        print_info(f"\n---> {cmd.upper()}")
        func = get_command(cmd)
        if func:
            exit_code = func(args)
            if exit_code == 0:
                results[cmd] = "PASS"
            elif exit_code == 1:
                results[cmd] = "FAIL"
            else:
                results[cmd] = "WARN"
                
    print_info("\n" + "=" * 40)
    print_info("DOCTOR SUMMARY")
    print_info("=" * 40)
    
    errors = 0
    warnings = 0
    for cmd, status in results.items():
        if status == "PASS":
            print_success(f"{cmd.ljust(25)} {status}")
        elif status == "WARN":
            print_warning(f"{cmd.ljust(25)} {status}")
            warnings += 1
        else:
            print_error(f"{cmd.ljust(25)} {status}")
            errors += 1
    
    if errors > 0:
        print_error(f"\nDoctor finished with {errors} failures and {warnings} warnings.")
        return 1
    elif warnings > 0:
        print_warning(f"\nDoctor finished with {warnings} warnings. Project is mostly healthy.")
        return 0
    else:
        print_success("\nDoctor finished. Your project is perfectly healthy!")
        return 0
