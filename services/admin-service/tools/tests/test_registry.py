import pytest
from tools.core.registry import register_command, get_command, get_all_commands, COMMAND_REGISTRY

def test_register_and_get_command():
    # Store original state to not pollute the global registry
    original_commands = dict(COMMAND_REGISTRY)
    COMMAND_REGISTRY.clear()
    
    @register_command("test-hyphen-cmd")
    def dummy_func(args):
        return 42
        
    func = get_command("test-hyphen-cmd")
    assert func is not None
    assert func(None) == 42
    
    assert "test-hyphen-cmd" in get_all_commands()
    
    # Restore global state
    COMMAND_REGISTRY.clear()
    COMMAND_REGISTRY.update(original_commands)

def test_get_unknown_command():
    func = get_command("non-existent-cmd")
    assert func is None
