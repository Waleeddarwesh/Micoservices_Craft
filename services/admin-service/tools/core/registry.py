# Command registry mapping hyphenated commands to functions
COMMAND_REGISTRY = {}

def register_command(name):
    """Decorator to register a CLI command."""
    def decorator(func):
        COMMAND_REGISTRY[name] = func
        return func
    return decorator

def get_command(name):
    return COMMAND_REGISTRY.get(name)

def get_all_commands():
    return list(COMMAND_REGISTRY.keys())
