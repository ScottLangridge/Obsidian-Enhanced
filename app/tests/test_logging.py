"""Tests for logging functionality"""

import pytest
import logging
from pathlib import Path
import re


class TestConsoleOutput:
    """Test that logs are properly formatted and emitted to logging system"""

    def test_server_logger_outputs_to_console(self, caplog):
        """Server logger outputs to console"""
        from logging_config import get_logger
        logger = get_logger("SERVER")

        test_message = "TestConsoleOutput_server_test_message_12345"

        with caplog.at_level(logging.INFO):
            logger.info(test_message)

        assert test_message in caplog.text
        assert "SERVER" in caplog.text

    def test_quick_capture_logger_outputs_to_console(self, caplog):
        """QuickCapture logger outputs to console"""
        from logging_config import get_logger
        logger = get_logger("QUICK_CAPTURE")

        test_message = "TestConsoleOutput_quick_capture_test_message_67890"

        with caplog.at_level(logging.INFO):
            logger.info(test_message)

        assert test_message in caplog.text
        assert "QUICK_CAPTURE" in caplog.text

    def test_vault_handler_logger_outputs_to_console(self, caplog):
        """VaultHandler logger outputs to console"""
        from logging_config import get_logger
        logger = get_logger("VAULT_HANDLER")

        test_message = "TestConsoleOutput_vault_handler_test_message_11111"

        with caplog.at_level(logging.INFO):
            logger.info(test_message)

        assert test_message in caplog.text
        assert "VAULT_HANDLER" in caplog.text

    def test_log_format_contains_all_required_fields(self, caplog):
        """Log format contains timestamp, level, logger name, and message"""
        from logging_config import get_logger
        logger = get_logger("SERVER")

        test_message = "TestConsoleOutput_format_test_22222"

        with caplog.at_level(logging.INFO):
            logger.info(test_message)

        # caplog.text contains the formatted log output
        output = caplog.text

        # Check for log level
        assert "INFO" in output

        # Check for logger name
        assert "SERVER" in output

        # Check for message
        assert test_message in output

    def test_info_level_messages_appear_in_console(self, caplog):
        """INFO level messages appear in console"""
        from logging_config import get_logger
        logger = get_logger("SERVER")

        test_message = "TestConsoleOutput_info_level_33333"

        with caplog.at_level(logging.INFO):
            logger.info(test_message)

        assert test_message in caplog.text
        assert any(record.levelname == "INFO" for record in caplog.records)

    def test_warning_level_messages_appear_in_console(self, caplog):
        """WARNING level messages appear in console"""
        from logging_config import get_logger
        logger = get_logger("SERVER")

        test_message = "TestConsoleOutput_warning_level_44444"

        with caplog.at_level(logging.WARNING):
            logger.warning(test_message)

        assert test_message in caplog.text
        assert any(record.levelname == "WARNING" for record in caplog.records)


class TestFileOutput:
    """Test that logs are written to file"""

    def test_log_file_exists(self, log_file_path):
        """Log file exists at /app/logs/app.log"""
        assert log_file_path.exists()

    def test_all_component_loggers_write_to_file(self, log_file_path):
        """All component loggers write to file"""
        from logging_config import get_logger

        # Generate unique test messages for each logger
        server_msg = "TestFileOutput_server_file_test_55555"
        quick_capture_msg = "TestFileOutput_quick_capture_file_test_66666"
        vault_handler_msg = "TestFileOutput_vault_handler_file_test_77777"

        # Log from each component
        get_logger("SERVER").info(server_msg)
        get_logger("QUICK_CAPTURE").info(quick_capture_msg)
        get_logger("VAULT_HANDLER").info(vault_handler_msg)

        # Read file and verify all messages are present
        content = log_file_path.read_text()
        assert server_msg in content
        assert quick_capture_msg in content
        assert vault_handler_msg in content

    def test_log_file_format_matches_expected_pattern(self, log_file_path):
        """Log file format matches expected pattern"""
        from logging_config import get_logger

        test_message = "TestFileOutput_format_test_88888"
        get_logger("SERVER").info(test_message)

        content = log_file_path.read_text()

        # Find the line with our test message
        lines = [line for line in content.split('\n') if test_message in line]
        assert len(lines) > 0

        log_line = lines[0]

        # Check format: timestamp - level - [logger] - message
        assert re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}', log_line)
        assert "INFO" in log_line
        assert "[SERVER]" in log_line
        assert test_message in log_line

    def test_file_appends_multiple_log_calls(self, log_file_path):
        """File appends (multiple log calls accumulate)"""
        from logging_config import get_logger
        logger = get_logger("SERVER")

        # Get initial file size
        initial_content = log_file_path.read_text()
        initial_size = len(initial_content)

        # Log multiple messages
        msg1 = "TestFileOutput_append_test_msg1_99999"
        msg2 = "TestFileOutput_append_test_msg2_00000"
        logger.info(msg1)
        logger.info(msg2)

        # Verify file has grown and both messages are present
        new_content = log_file_path.read_text()
        assert len(new_content) > initial_size
        assert msg1 in new_content
        assert msg2 in new_content

    def test_logs_from_integration_appear_in_file(self, test_client, log_file_path):
        """Logs from integration tests appear in file"""
        test_text = "TestFileOutput_integration_aaaaa"

        # Make API request
        response = test_client.post("/api/capture", json={"text": test_text})
        assert response.status_code == 200

        # Check file for logged message
        content = log_file_path.read_text()
        assert f"Received: {test_text}" in content


class TestIntegrationLogging:
    """Test full logging flow with API integration"""

    def test_capture_endpoint_logs_to_console_and_file(self, test_client, caplog, log_file_path):
        """Capture endpoint logs to both console and file"""
        test_text = "TestIntegration_capture_endpoint_bbbbb"

        # Make API request
        with caplog.at_level(logging.INFO):
            response = test_client.post("/api/capture", json={"text": test_text})
        assert response.status_code == 200

        # Check logs were emitted
        assert f"Received: {test_text}" in caplog.text

        # Check file
        file_content = log_file_path.read_text()
        assert f"Received: {test_text}" in file_content

    def test_parking_level_rule_match_logging(self, test_client, caplog, log_file_path):
        """Parking level rule match logs correctly (SERVER + QUICK_CAPTURE logs)"""
        test_text = "pl7"

        # Make API request
        with caplog.at_level(logging.INFO):
            response = test_client.post("/api/capture", json={"text": test_text})
        assert response.status_code == 200

        # Check console for both SERVER and QUICK_CAPTURE logs
        assert f"Received: {test_text}" in caplog.text  # SERVER log
        assert "Processing:" in caplog.text  # QUICK_CAPTURE log
        assert "Matched rule:" in caplog.text  # QUICK_CAPTURE log

        # Check file
        file_content = log_file_path.read_text()
        assert f"Received: {test_text}" in file_content
        assert "Processing:" in file_content

    def test_fallback_handler_logs_warning(self, test_client, caplog, log_file_path):
        """Fallback handler logs warning message"""
        test_text = "TestIntegration_fallback_ccccc_no_match"

        # Make API request with text that won't match any rule
        with caplog.at_level(logging.WARNING):
            response = test_client.post("/api/capture", json={"text": test_text})
        assert response.status_code == 200

        # Check console for warning
        assert "No rule matched - using fallback" in caplog.text
        assert any(record.levelname == "WARNING" for record in caplog.records)

        # Check file for warning
        file_content = log_file_path.read_text()
        assert "No rule matched - using fallback" in file_content

    def test_multiple_captures_accumulate_in_both_outputs(self, test_client, caplog, log_file_path):
        """Multiple captures accumulate in both outputs"""
        test_text1 = "TestIntegration_multiple_1_ddddd"
        test_text2 = "TestIntegration_multiple_2_eeeee"

        # Make multiple requests
        with caplog.at_level(logging.INFO):
            response1 = test_client.post("/api/capture", json={"text": test_text1})
            assert response1.status_code == 200

            response2 = test_client.post("/api/capture", json={"text": test_text2})
            assert response2.status_code == 200

        # Check logs have both
        assert f"Received: {test_text1}" in caplog.text
        assert f"Received: {test_text2}" in caplog.text

        # Check file has both
        file_content = log_file_path.read_text()
        assert f"Received: {test_text1}" in file_content
        assert f"Received: {test_text2}" in file_content
