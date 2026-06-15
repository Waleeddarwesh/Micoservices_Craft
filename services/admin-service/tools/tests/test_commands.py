import pytest
import argparse
from unittest.mock import patch, MagicMock
from tools.commands.devops import run_doctor, run_pre_deploy

class MockArgs:
    def __init__(self, dry_run=False, yes=False):
        self.dry_run = dry_run
        self.yes = yes

@patch("tools.commands.devops.get_command")
def test_doctor_all_pass(mock_get_command):
    # Mock all commands to return 0 (success)
    mock_func = MagicMock(return_value=0)
    mock_get_command.return_value = mock_func
    
    args = MockArgs()
    exit_code = run_doctor(args)
    assert exit_code == 0

@patch("tools.commands.devops.get_command")
def test_doctor_with_failures(mock_get_command):
    def side_effect(cmd_name):
        if cmd_name == "check-env":
            return MagicMock(return_value=1) # FAIL
        if cmd_name == "docker-check":
            return MagicMock(return_value=2) # WARN (blocked)
        return MagicMock(return_value=0) # PASS
        
    mock_get_command.side_effect = side_effect
    
    args = MockArgs()
    exit_code = run_doctor(args)
    assert exit_code == 1 # Doctor should fail if there are any failures

@patch("tools.commands.devops.get_command")
def test_pre_deploy_fails_fast(mock_get_command):
    def side_effect(cmd_name):
        # We fail at check-services
        if cmd_name == "check-services":
            return MagicMock(return_value=1)
        return MagicMock(return_value=0)
        
    mock_get_command.side_effect = side_effect
    
    args = MockArgs()
    exit_code = run_pre_deploy(args)
    assert exit_code == 1
