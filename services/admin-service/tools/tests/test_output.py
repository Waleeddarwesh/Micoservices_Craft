import logging
import pytest
from tools.core.output import setup_output, logger

def test_setup_output_quiet():
    setup_output(quiet=True, verbose=False)
    assert logger.level == logging.CRITICAL

def test_setup_output_verbose():
    setup_output(quiet=False, verbose=True)
    assert logger.level == logging.DEBUG

def test_setup_output_default():
    setup_output(quiet=False, verbose=False)
    assert logger.level == logging.INFO

def test_setup_output_priority():
    # If both quiet and verbose are passed, quiet should win according to logic
    setup_output(quiet=True, verbose=True)
    assert logger.level == logging.CRITICAL
