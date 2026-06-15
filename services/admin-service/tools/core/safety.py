import os
import sys
from tools.core.output import print_error, print_warning, print_info

DANGEROUS_COMMANDS = {
    "db-reset",
    "generate-dummy-data",
    "upgrade-user",
    "setup-ops-teams",
    "assign-group-permissions",
}

def is_production():
    production_values = {"production", "prod", "live"}

    env_vars = [
        os.getenv("DJANGO_ENV"),
        os.getenv("ENVIRONMENT"),
        os.getenv("APP_ENV"),
        os.getenv("RAILWAY_ENVIRONMENT"),
    ]

    if any(value and value.lower() in production_values for value in env_vars):
        return True

    return False

def prevent_production(command_name=None):
    """
    Checks if running in production.
    Returns 2 if blocked, 0 if safe to proceed.
    """
    if is_production():
        print_error(f"Command blocked in production: {command_name or 'unknown'}")
        return 2
    return 0

def confirm_dangerous_action(action_name, yes_flag=False):
    """
    Prompts for confirmation unless yes_flag is True.
    Returns 0 if confirmed, 1 if cancelled.
    """
    if yes_flag:
        print_warning(f"Auto-confirming dangerous action ({action_name}) because --yes was passed.")
        return 0

    expected = action_name.upper()
    value = input(f"Type {expected} to confirm {action_name}: ")
    
    if value != expected:
        print_info("Cancelled.")
        return 1
        
    return 0
