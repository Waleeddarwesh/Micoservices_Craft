import os
import sys
import shutil
from datetime import datetime

from tools.core.registry import register_command
from tools.core.safety import prevent_production, confirm_dangerous_action
from tools.core.output import print_info, print_success, print_error

@register_command("db-reset")
def run_db_reset(args):
    exit_code = prevent_production("db-reset")
    if exit_code != 0:
        return exit_code
        
    if confirm_dangerous_action("db-reset", args.yes) != 0:
        return 1
        
    if args.dry_run:
        print_info("Would delete db.sqlite3")
        print_info("Would run migrations")
        print_info("Would setup ops teams")
        print_info("Would assign group permissions")
        print_info("No database changes were applied.")
        return 0
    
    import subprocess
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "db.sqlite3")
    if os.path.exists(db_path):
        os.remove(db_path)
        print_success("Deleted db.sqlite3")
    else:
        print_info("db.sqlite3 not found, skipping delete.")
    
    print_info("Running migrations...")
    try:
        subprocess.run([sys.executable, "manage.py", "migrate"], check=True)
        print_success("Migrations complete.")
    except Exception as e:
        print_error(f"Migrations failed: {e}")
        return 1
    
    from tools.commands.ops import _do_setup_ops_teams, _do_assign_group_permissions
    print_info("Setting up ops teams...")
    _do_setup_ops_teams(args)
    print_info("Assigning group permissions...")
    _do_assign_group_permissions(args)
    print_success("Database reset successful!")
    return 0

@register_command("backup-db")
def run_backup_db(args):
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "db.sqlite3")

    if not os.path.exists(db_path):
        print_error("db.sqlite3 not found.")
        return 1

    backup_name = f"db_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sqlite3"
    backup_path = os.path.join(os.path.dirname(db_path), backup_name)

    if args.dry_run:
        print_info(f"Would create backup: {backup_path}")
        return 0

    try:
        shutil.copy2(db_path, backup_path)
        print_success(f"Backup created: {backup_path}")
        return 0
    except Exception as e:
        print_error(f"Backup failed: {e}")
        return 1

@register_command("check-migrations")
def run_check_migrations(args):
    from tools.django_setup import setup_django
    setup_django()

    from django.core.management import call_command

    print_info("Checking for missing migrations...")
    try:
        call_command("makemigrations", "--check", "--dry-run")
        print_success("No missing migrations.")
    except SystemExit:
        print_error("Missing migrations detected.")
        return 1

    print_info("Checking migration plan...")
    call_command("showmigrations", "--plan")
    return 0
