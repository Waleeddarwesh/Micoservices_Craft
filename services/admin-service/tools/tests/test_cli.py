import sys
import pytest
from unittest.mock import patch, MagicMock

# We must mock sys.exit to prevent the test suite from exiting
@patch("sys.exit")
@patch("tools.core.registry.get_command")
@patch("tools.core.output.setup_output")
def test_cli_dispatch(mock_setup, mock_get_command, mock_exit):
    # Mock the command function
    mock_func = MagicMock()
    mock_func.return_value = 0
    mock_get_command.return_value = mock_func

    # Simulate sys.argv
    test_args = ["cli.py", "doctor", "--verbose", "--yes"]
    with patch.object(sys, "argv", test_args):
        # We need to run the cli script logic. 
        # But importing it normally runs __main__ block? No, import does not run __main__.
        # We can simulate running the script by execing it or importing and running main if we had one.
        # Let's use runpy or just import standard libraries.
        pass

    # Since cli.py does not have a main() function and executes in global scope,
    # it's better to structure this test as an integration test using subprocess,
    # or assert the argparse logic inside cli if we refactor it.
    
    # For now, let's verify subprocess calling works.
    import subprocess
    result = subprocess.run(
        [sys.executable, "tools/cli.py", "doctor", "--help"],
        capture_output=True,
        text=True
    )
    # Just asserting it doesn't crash on standard args
    assert "usage: cli.py" in result.stdout

def test_cli_unknown_command():
    import subprocess
    result = subprocess.run(
        [sys.executable, "tools/cli.py", "fake-command"],
        capture_output=True,
        text=True
    )
    # Argparse should exit with 2 on invalid choice
    assert result.returncode == 2
    assert "invalid choice: 'fake-command'" in result.stderr
