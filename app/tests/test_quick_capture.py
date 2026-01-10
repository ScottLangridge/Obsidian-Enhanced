"""Tests for QuickCapture rule matching and text processing"""

import pytest
from unittest.mock import MagicMock


class TestParkingLevelPattern:
    """Test parking level pattern matching (pl1-pl9, case-insensitive, whitespace handling)"""

    def test_parking_level_basic(self, quick_capture_instance, mock_vault_handler):
        """Parking Level (Basic): 'pl3' formats to 'Parking Level: 3'"""
        quick_capture_instance.process("pl3")
        mock_vault_handler.append_to_daily_note.assert_called_once_with("Parking Level: 3")

    def test_parking_level_multiple_digits(self, quick_capture_instance, mock_vault_handler):
        """Parking Level (Multiple Digits): Handle multiple digits like 'pl999'

        Note: Current regex only captures single digit (\d), so this should go to fallback
        """
        quick_capture_instance.process("pl999")
        # Based on current regex r'\s*pl(\d)\s*', this should NOT match and go to fallback
        # The regex only captures one digit, so "pl999" won't match
        mock_vault_handler.append_to_daily_note.assert_called_once_with("pl999")

    def test_parking_level_all_single_digits(self, quick_capture_instance, mock_vault_handler):
        """Parking Level (All Single Digits): All digits 1-9 work correctly"""
        for digit in range(1, 10):
            mock_vault_handler.reset_mock()
            text = f"pl{digit}"
            quick_capture_instance.process(text)
            mock_vault_handler.append_to_daily_note.assert_called_once_with(f"Parking Level: {digit}")

    def test_parking_level_case_insensitive_uppercase(self, quick_capture_instance, mock_vault_handler):
        """Parking Level (Case Insensitive - Uppercase): 'PL3' formats correctly"""
        quick_capture_instance.process("PL3")
        mock_vault_handler.append_to_daily_note.assert_called_once_with("Parking Level: 3")

    def test_parking_level_case_insensitive_mixed(self, quick_capture_instance, mock_vault_handler):
        """Parking Level (Case Insensitive - Mixed): 'Pl3' formats correctly"""
        quick_capture_instance.process("Pl3")
        mock_vault_handler.append_to_daily_note.assert_called_once_with("Parking Level: 3")

    def test_parking_level_whitespace_trimming(self, quick_capture_instance, mock_vault_handler):
        """Parking Level (Whitespace Trimming): ' pl3 ' with leading/trailing whitespace formats correctly"""
        quick_capture_instance.process(" pl3 ")
        mock_vault_handler.append_to_daily_note.assert_called_once_with("Parking Level: 3")

    def test_parking_level_whitespace_with_newlines(self, quick_capture_instance, mock_vault_handler):
        """Parking Level (Whitespace With Newlines): ' \\n pl3 \\n ' with whitespace formats correctly"""
        quick_capture_instance.process(" \n pl3 \n ")
        mock_vault_handler.append_to_daily_note.assert_called_once_with("Parking Level: 3")


class TestFallbackHandler:
    """Test fallback handler for unmatched text"""

    def test_fallback_unmatched_text(self, quick_capture_instance, mock_vault_handler):
        """Fallback (Unmatched Text): Text that doesn't match any rule goes to fallback handler"""
        quick_capture_instance.process("Random unmatched text")
        mock_vault_handler.append_to_daily_note.assert_called_once_with("Random unmatched text")

    def test_fallback_special_characters(self, quick_capture_instance, mock_vault_handler):
        """Fallback (Special Characters): Special characters are handled correctly"""
        text = "Special chars: !@#$%^&*()_+-=[]{}|;':,.<>?/"
        quick_capture_instance.process(text)
        mock_vault_handler.append_to_daily_note.assert_called_once_with(text)

    def test_fallback_unicode(self, quick_capture_instance, mock_vault_handler):
        """Fallback (Unicode): Unicode characters are handled correctly"""
        text = "Unicode: 你好世界 🚗 café naïve"
        quick_capture_instance.process(text)
        mock_vault_handler.append_to_daily_note.assert_called_once_with(text)


class TestRuleMatchingLogic:
    """Test rule matching logic and ordering"""

    def test_rule_matching_first_match_wins(self, mock_vault_handler):
        """Rule Matching (First Match Wins): When multiple rules could match, first match is used"""
        from quick_capture import QuickCapture

        # Create a QuickCapture instance and add overlapping rules
        qc = QuickCapture(mock_vault_handler)

        # The current implementation has parking level as first rule
        # Process text that matches parking level pattern
        qc.process("pl5")

        # Should call the parking level handler, not fallback
        mock_vault_handler.append_to_daily_note.assert_called_once_with("Parking Level: 5")

    def test_rule_matching_order(self, mock_vault_handler):
        """Rule Matching (Order): Rules are processed in the order they are defined"""
        from quick_capture import QuickCapture

        qc = QuickCapture(mock_vault_handler)

        # Verify that rules list exists and is ordered
        assert hasattr(qc, 'rules')
        assert isinstance(qc.rules, list)
        assert len(qc.rules) > 0

        # First rule should be parking level pattern
        first_pattern, first_handler = qc.rules[0]
        assert first_handler.__name__ == 'handle_parking_level'

    def test_rule_matching_handler_routing(self, mock_vault_handler):
        """Rule Matching (Handler Routing): Matched rule routes to correct handler"""
        from quick_capture import QuickCapture

        qc = QuickCapture(mock_vault_handler)

        # Test parking level routing
        qc.process("pl7")
        mock_vault_handler.append_to_daily_note.assert_called_once_with("Parking Level: 7")

        # Test fallback routing
        mock_vault_handler.reset_mock()
        qc.process("Some other text")
        mock_vault_handler.append_to_daily_note.assert_called_once_with("Some other text")
