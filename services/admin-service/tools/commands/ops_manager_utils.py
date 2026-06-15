import os
import sys
import time
from tabulate import tabulate
from tools.core.output import print_info, print_success, print_error
from tools.commands.ops import print_header, get_input, generate_random_password, clear_screen

def ops_list_teams():
    from django.contrib.auth.models import Group
    print_header("Existing Operational Teams")
    groups = Group.objects.all()
    if not groups.exists():
        print_info("No teams found.")
    else:
        table = [[g.id, g.name, g.user_set.count()] for g in groups]
        print(tabulate(table, headers=["ID", "Team Name", "Users"], tablefmt="grid"))
    input("\nPress Enter to continue...")

def ops_create_team():
    from django.contrib.auth.models import Group, Permission
    print_header("Create New Team")
    name = get_input("  Enter team name (e.g., Sales, Support, Admins): ")
    group, created = Group.objects.get_or_create(name=name)
    if created:
        print_success(f"Team '{name}' created successfully!")
    else:
        print_info(f"Team '{name}' already exists.")
        
    assign = get_input("\n  Assign dashboard permissions to this team? (y/n): ").lower()
    if assign == 'y':
        perms = Permission.objects.filter(content_type__app_label='accounts')
        print_info("Available Custom Permissions:")
        for idx, p in enumerate(perms, 1):
            print(f"    {idx}. {p.name}")
        choices = get_input("\n  Enter permission numbers separated by comma (e.g., 1,3,5), or 'all': ")
        if choices.lower() == 'all':
            group.permissions.set(perms)
            print_success("All permissions assigned.")
        else:
            try:
                selected_indices = [int(c.strip()) - 1 for c in choices.split(',')]
                selected_perms = [perms[i] for i in selected_indices if 0 <= i < len(perms)]
                group.permissions.set(selected_perms)
                print_success(f"{len(selected_perms)} permissions assigned.")
            except Exception as e:
                print_error("Invalid input. No permissions assigned.")
    input("\nPress Enter to continue...")

def ops_create_user():
    from django.contrib.auth.models import Group
    from accounts.models import User
    print_header("Create Operational User")
    email = get_input("  Email address: ")
    if User.objects.filter(email=email).exists():
        print_error("A user with this email already exists.")
        input("\nPress Enter to continue...")
        return
        
    first_name = get_input("  First Name: ")
    last_name = get_input("  Last Name: ")
    phone = get_input("  Phone Number (optional): ", required=False)
    
    print("\n  [ Password Generation ]")
    print("  1. Auto-generate secure password")
    print("  2. Enter manually")
    pass_choice = get_input("  Choice (1/2): ")
    if pass_choice == '2':
        password = get_input("  Enter password: ")
    else:
        password = generate_random_password()
        print_info(f"Generated Password: {password}")
        print_info("Make sure to share this with the user safely.")
        
    print("\n  [ Team Assignment ]")
    groups = list(Group.objects.all())
    if groups:
        for idx, g in enumerate(groups, 1):
            print(f"  {idx}. {g.name}")
        print("  0. Skip team assignment")
        try:
            team_choice = int(get_input("\n  Select Team Number: "))
            selected_team = groups[team_choice - 1] if team_choice > 0 else None
        except:
            selected_team = None
    else:
        print_info("No teams exist yet.")
        selected_team = None
        
    user = User(
        email=email.lower(),
        first_name=first_name,
        last_name=last_name,
        PhoneNO=phone,
        is_staff=True,
        is_verified=True,
        must_change_password=True
    )
    user.set_password(password)
    user.save()
    
    if selected_team:
        user.groups.add(selected_team)
        team_msg = f"assigned to {selected_team.name}"
    else:
        team_msg = "no team assigned"
        
    print_success(f"User created successfully ({team_msg})!")
    print_success("The user will be forced to change their password on first login.")
    input("\nPress Enter to continue...")

def main_menu():
    while True:
        clear_screen()
        print_header("Company Operations Manager")
        print("  1. List existing teams")
        print("  2. Create a new team & assign permissions")
        print("  3. Create a new operational user")
        print("  4. Exit")
        choice = input("\n  Select an option (1-4): ").strip()
        if choice == '1':
            ops_list_teams()
        elif choice == '2':
            ops_create_team()
        elif choice == '3':
            ops_create_user()
        elif choice == '4':
            print_info("Exiting. Goodbye!")
            sys.exit(0)
        else:
            print_error("Invalid choice.")
            time.sleep(1)
