#!/usr/bin/env python3

"""
End-to-end test for logging functionality.
This test verifies that:
1. Log files are created
2. Logs appear in both console and file
3. Log format is correct
4. All components log correctly
"""

import sys
import time
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "app"))


def test_logging_setup_and_file_creation():
    """Test that logging setup works and creates log file"""
    import logging
    from logging_config import setup_logging

    # Clear any existing handlers
    logging.getLogger().handlers.clear()

    # Setup logging
    loggers = setup_logging()

    # Verify loggers exist
    assert "SERVER" in loggers
    assert "QUICK_CAPTURE" in loggers
    assert "VAULT_HANDLER" in loggers

    # Log a test message
    loggers["SERVER"].info("E2E test message")

    # Force flush
    for handler in logging.getLogger().handlers:
        handler.flush()

    # Wait a moment for file to be written
    time.sleep(0.1)

    # Check log file exists
    log_file = Path("/app/logs/app.log")
    assert log_file.exists(), f"Log file not found at {log_file}"

    # Verify content
    with open(log_file, "r") as f:
        content = f.read()
        assert "E2E test message" in content, "Test message not found in log file"
        assert "[SERVER]" in content, "Logger name not in log file"


def test_complete_logging_flow():
    """Test complete logging flow through all components"""
    import logging
    from logging_config import setup_logging
    from vault_handler import VaultHandler
    from quick_capture import QuickCapture

    # Clear any existing handlers
    logging.getLogger().handlers.clear()

    # Setup logging
    setup_logging()

    # Create components
    vh = VaultHandler("/vault")
    qc = QuickCapture(vh)

    # Process some test data
    qc.process("pl3")
    qc.process("Random text")

    # Force flush all handlers
    for handler in logging.getLogger().handlers:
        handler.flush()

    # Wait for writes
    time.sleep(0.1)

    # Verify log file exists and contains expected entries
    log_file = Path("/app/logs/app.log")
    assert log_file.exists(), "Log file not created"

    with open(log_file, "r") as f:
        content = f.read()

        # Verify QuickCapture logging
        assert "[QUICK_CAPTURE]" in content, "QUICK_CAPTURE logger not found"
        assert "Processing: pl3" in content, "Processing message not logged"
        assert "Matched rule:" in content, "Rule match not logged"

        # Verify VaultHandler logging
        assert "[VAULT_HANDLER]" in content, "VAULT_HANDLER logger not found"
        assert "Appending to daily note:" in content, "Append message not logged"
        assert "Parking Level: 3" in content, "Formatted parking level not logged"

        # Verify fallback warning
        assert "WARNING" in content, "WARNING level not found"
        assert "No rule matched - using fallback" in content, "Fallback warning not logged"


def test_log_format_correct():
    """Verify log format matches specification"""
    import logging
    from logging_config import setup_logging

    # Clear handlers
    logging.getLogger().handlers.clear()

    # Setup logging
    loggers = setup_logging()

    # Log a message
    loggers["SERVER"].info("Format test")

    # Force flush
    for handler in logging.getLogger().handlers:
        handler.flush()

    time.sleep(0.1)

    # Read log file
    log_file = Path("/app/logs/app.log")
    with open(log_file, "r") as f:
        lines = f.readlines()

    # Find our test message
    test_line = None
    for line in lines:
        if "Format test" in line:
            test_line = line
            break

    assert test_line is not None, "Test message not found in logs"

    # Verify format: YYYY-MM-DD HH:MM:SS,mmm - LEVEL - [NAME] - message
    import re
    pattern = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3} - INFO - \[SERVER\] - Format test'
    assert re.search(pattern, test_line), f"Log format incorrect: {test_line}"


if __name__ == "__main__":
    print("Running E2E logging tests...")

    try:
        test_logging_setup_and_file_creation()
        print("✓ Test 1: Logging setup and file creation - PASSED")
    except AssertionError as e:
        print(f"✗ Test 1 FAILED: {e}")
        sys.exit(1)

    try:
        test_complete_logging_flow()
        print("✓ Test 2: Complete logging flow - PASSED")
    except AssertionError as e:
        print(f"✗ Test 2 FAILED: {e}")
        sys.exit(1)

    try:
        test_log_format_correct()
        print("✓ Test 3: Log format - PASSED")
    except AssertionError as e:
        print(f"✗ Test 3 FAILED: {e}")
        sys.exit(1)

    print("\nAll E2E logging tests PASSED! ✓")
