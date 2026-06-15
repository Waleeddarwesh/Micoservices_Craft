import os
import pytest
from unittest.mock import patch, MagicMock
from tools.core.safety import is_production, prevent_production, confirm_dangerous_action

@pytest.fixture
def clean_env():
    # Remove variables that might trigger production detection
    vars_to_clear = ["DJANGO_ENV", "ENVIRONMENT", "APP_ENV", "RAILWAY_ENVIRONMENT", "DEBUG"]
    old_env = {}
    for v in vars_to_clear:
        old_env[v] = os.environ.get(v)
        if v in os.environ:
            del os.environ[v]
            
    yield
    
    for v, val in old_env.items():
        if val is not None:
            os.environ[v] = val
        elif v in os.environ:
            del os.environ[v]

def test_is_production_true(clean_env):
    os.environ["DJANGO_ENV"] = "production"
    assert is_production() is True
    
    os.environ["DJANGO_ENV"] = "development"
    os.environ["RAILWAY_ENVIRONMENT"] = "prod"
    assert is_production() is True

def test_is_production_false(clean_env):
    os.environ["DJANGO_ENV"] = "development"
    assert is_production() is False
    
    # DEBUG=False alone should not trigger production blocking
    os.environ["DEBUG"] = "False"
    assert is_production() is False

@patch("tools.core.safety.is_production")
@patch("tools.core.safety.print_error")
def test_prevent_production(mock_print_error, mock_is_prod):
    mock_is_prod.return_value = True
    assert prevent_production("dangerous-cmd") == 2
    mock_print_error.assert_called_once()
    
    mock_is_prod.return_value = False
    assert prevent_production("dangerous-cmd") == 0

@patch("builtins.input")
@patch("tools.core.safety.print_info")
def test_confirm_dangerous_action_yes_flag(mock_print_info, mock_input):
    # Should bypass input prompt
    assert confirm_dangerous_action("db-reset", yes_flag=True) == 0
    mock_input.assert_not_called()

@patch("builtins.input")
def test_confirm_dangerous_action_success(mock_input):
    mock_input.return_value = "DB-RESET"
    assert confirm_dangerous_action("db-reset", yes_flag=False) == 0

@patch("builtins.input")
def test_confirm_dangerous_action_cancel(mock_input):
    mock_input.return_value = "yes"  # Incorrect, expecting DB-RESET
    assert confirm_dangerous_action("db-reset", yes_flag=False) == 1
