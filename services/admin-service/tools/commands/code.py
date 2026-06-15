import os
import re

from tools.core.registry import register_command
from tools.core.output import print_info, print_success, print_error

@register_command("find-missing-translations")
def run_find_missing(args):
    js_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'dashboard', 'js')
    found_keys = set()
    for root, _, files in os.walk(js_dir):
        for f in files:
            if f.endswith('.js'):
                with open(os.path.join(root, f), 'r', encoding='utf-8') as file:
                    content = file.read()
                    matches = re.findall(r'window\.t\(([\'\"`])(.*?)\1\)', content)
                    for quote, key in matches:
                        found_keys.add(key)
    try:
        with open(os.path.join(js_dir, 'i18n.js'), 'r', encoding='utf-8') as file:
            i18n_content = file.read()
    except FileNotFoundError:
        print_error(f"Could not find i18n.js in {js_dir}")
        return 1

    missing_keys = []
    for key in sorted(found_keys):
        if f'"{key}":' not in i18n_content and f"'{key}':" not in i18n_content:
            missing_keys.append(key)
            
    if missing_keys:
        print_error('Missing keys:')
        for k in missing_keys:
            print_error(k)
        return 1
    else:
        print_success("No missing translation keys found.")
        return 0

@register_command("list-urls")
def run_list_urls(args):
    from tools.django_setup import setup_django
    setup_django()

    from django.urls import get_resolver, URLPattern, URLResolver

    def walk_patterns(patterns, prefix=""):
        for pattern in patterns:
            if isinstance(pattern, URLPattern):
                print_info(f"{prefix}{pattern.pattern}  ->  {pattern.name}")
            elif isinstance(pattern, URLResolver):
                walk_patterns(pattern.url_patterns, prefix + str(pattern.pattern))

    resolver = get_resolver()
    walk_patterns(resolver.url_patterns)
    return 0

@register_command("check-static")
def run_check_static(args):
    from tools.django_setup import setup_django
    setup_django()

    from django.core.management import call_command

    try:
        call_command("collectstatic", "--noinput", "--dry-run")
        print_success("Static files check completed.")
        return 0
    except Exception as e:
        print_error(f"Static files check failed: {e}")
        return 1

@register_command("check-imports")
def run_check_imports(args):
    import py_compile

    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    errors = []

    for root, dirs, files in os.walk(base_dir):
        dirs[:] = [d for d in dirs if d not in {".git", ".venv", "venv", "__pycache__"}]

        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                try:
                    py_compile.compile(path, doraise=True)
                except Exception as e:
                    errors.append((path, e))

    if errors:
        print_error("Python files with syntax/import compile errors:")
        for path, error in errors:
            print_error(f"- {path}: {error}")
        return 1
    else:
        print_success("All Python files compiled successfully.")
        return 0

@register_command("clean-cache")
def run_clean_cache(args):
    if args.dry_run:
        print_info("Would delete __pycache__ directories and .pyc files.")
        return 0
        
    import shutil
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    count_dirs = 0
    count_files = 0
    for root, dirs, files in os.walk(base_dir):
        if "__pycache__" in dirs:
            shutil.rmtree(os.path.join(root, "__pycache__"))
            dirs.remove("__pycache__")
            count_dirs += 1
        for f in files:
            if f.endswith(".pyc") or f.endswith(".pyo"):
                os.remove(os.path.join(root, f))
                count_files += 1
                
    print_success(f"Cache cleaned: Removed {count_dirs} __pycache__ directories and {count_files} compiled files.")
    return 0
