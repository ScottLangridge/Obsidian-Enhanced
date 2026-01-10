#!/usr/bin/env python3

import pytest
import sys
import logging
from pathlib import Path
from io import StringIO

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "app"))


def test_no_print_statements_in_codebase():
    """Verify no print() statements remain in the codebase"""
    app_dir = Path(__file__).parent.parent / "app"

    # List of Python files to check
    python_files = list(app_dir.glob("*.py"))

    for file_path in python_files:
        with open(file_path, "r") as f:
            content = f.read()
            # Check if file contains print statements (excluding comments and docstrings)
            lines = content.split("\n")
            for i, line in enumerate(lines, start=1):
                # Skip comments and docstrings
                stripped = line.strip()
                if stripped.startswith("#"):
                    continue
                if 'print(' in line and not line.strip().startswith('"""') and not line.strip().startswith("'''"):
                    # Verify it's not in a comment
                    code_part = line.split("#")[0]
                    if 'print(' in code_part:
                        pytest.fail(f"Found print() statement in {file_path}:{i}: {line}")


def test_logging_modules_use_correct_loggers():
    """Test that each module uses its own logger"""
    from quick_capture import logger as qc_logger
    from vault_handler import logger as vh_logger
    from server import logger as server_logger

    assert qc_logger.name == "QUICK_CAPTURE"
    assert vh_logger.name == "VAULT_HANDLER"
    assert server_logger.name == "SERVER"


def test_logging_config_get_logger():
    """Test get_logger function returns correct logger"""
    from logging_config import get_logger

    logger = get_logger("TEST")
    assert isinstance(logger, logging.Logger)
    assert logger.name == "TEST"


def test_log_format():
    """Test that log format matches specification"""
    from logging_config import LOG_FORMAT

    # Create a simple logger to test format
    logger = logging.getLogger("FORMAT_TEST")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    # Create a string handler to capture output
    log_stream = StringIO()
    handler = logging.StreamHandler(log_stream)
    formatter = logging.Formatter(LOG_FORMAT)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Log a test message
    logger.info("Test message")

    # Get logged output
    output = log_stream.getvalue()

    # Verify format includes timestamp, level, logger name, and message
    assert "INFO" in output
    assert "[FORMAT_TEST]" in output
    assert "Test message" in output

    # Check for timestamp format (YYYY-MM-DD HH:MM:SS,mmm)
    import re
    timestamp_pattern = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}'
    assert re.search(timestamp_pattern, output), f"Timestamp not found in: {output}"


def test_quick_capture_uses_logging(capfd):
    """Test that QuickCapture uses logging, not print"""
    # Import modules
    from vault_handler import VaultHandler
    from quick_capture import QuickCapture

    # Create instances
    vh = VaultHandler("/vault")
    qc = QuickCapture(vh)

    # Process text (this should log, not print)
    qc.process("pl3")

    # Capture stdout/stderr
    captured = capfd.readouterr()

    # Verify nothing was printed to stdout (all output should be via logging to stderr)
    assert captured.out == "", "QuickCapture should not print to stdout"


def test_vault_handler_uses_logging(capfd):
    """Test that VaultHandler uses logging, not print"""
    from vault_handler import VaultHandler

    # Create instance
    vh = VaultHandler("/vault")

    # Call method (this should log, not print)
    vh.append_to_daily_note("Test")

    # Capture stdout/stderr
    captured = capfd.readouterr()

    # Verify nothing was printed to stdout
    assert captured.out == "", "VaultHandler should not print to stdout"


def test_logging_levels():
    """Test that different log levels work correctly"""
    from logging_config import LOG_FORMAT

    # Create a test logger
    logger = logging.getLogger("LEVEL_TEST")
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()

    # Create a string handler to capture output
    log_stream = StringIO()
    handler = logging.StreamHandler(log_stream)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(LOG_FORMAT)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Log at different levels
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")

    # Get logged output
    output = log_stream.getvalue()

    # Verify all levels are present
    assert "DEBUG" in output
    assert "INFO" in output
    assert "WARNING" in output
    assert "ERROR" in output
    assert "Debug message" in output
    assert "Info message" in output
    assert "Warning message" in output
    assert "Error message" in output
