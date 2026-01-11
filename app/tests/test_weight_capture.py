"""Tests for weight capture pattern matching and tag population

Weight capture should:
- Match patterns: w70.3, weight 70.3, weight70.3
- Always format to 1 decimal place: w72 -> [weight::72.0]
- Populate the [weight::] tag in the Trackers section (NOT Quick Capture)
"""

import pytest
from unittest.mock import MagicMock


class TestWeightPattern:
    """Test weight pattern matching and formatting"""

    def test_weight_with_w_prefix_decimal(self, quick_capture_instance, mock_vault_handler):
        """Weight (w prefix with decimal): 'w70.3' populates [weight::70.3]"""
        quick_capture_instance.process("w70.3")
        mock_vault_handler.populate_weight_tag.assert_called_once_with("70.3")

    def test_weight_with_w_prefix_integer(self, quick_capture_instance, mock_vault_handler):
        """Weight (w prefix integer): 'w72' populates [weight::72.0]"""
        quick_capture_instance.process("w72")
        mock_vault_handler.populate_weight_tag.assert_called_once_with("72.0")

    def test_weight_with_w_prefix_multiple_decimal_places(self, quick_capture_instance, mock_vault_handler):
        """Weight (w prefix multiple decimals): 'w70.345' populates [weight::70.3]"""
        quick_capture_instance.process("w70.345")
        mock_vault_handler.populate_weight_tag.assert_called_once_with("70.3")

    def test_weight_with_word_prefix_space_decimal(self, quick_capture_instance, mock_vault_handler):
        """Weight (word prefix with space): 'weight 70.3' populates [weight::70.3]"""
        quick_capture_instance.process("weight 70.3")
        mock_vault_handler.populate_weight_tag.assert_called_once_with("70.3")

    def test_weight_with_word_prefix_space_integer(self, quick_capture_instance, mock_vault_handler):
        """Weight (word prefix with space integer): 'weight 72' populates [weight::72.0]"""
        quick_capture_instance.process("weight 72")
        mock_vault_handler.populate_weight_tag.assert_called_once_with("72.0")

    def test_weight_with_word_prefix_no_space_decimal(self, quick_capture_instance, mock_vault_handler):
        """Weight (word prefix no space): 'weight70.3' populates [weight::70.3]"""
        quick_capture_instance.process("weight70.3")
        mock_vault_handler.populate_weight_tag.assert_called_once_with("70.3")

    def test_weight_with_word_prefix_no_space_integer(self, quick_capture_instance, mock_vault_handler):
        """Weight (word prefix no space integer): 'weight72' populates [weight::72.0]"""
        quick_capture_instance.process("weight72")
        mock_vault_handler.populate_weight_tag.assert_called_once_with("72.0")

    def test_weight_case_insensitive_uppercase_w(self, quick_capture_instance, mock_vault_handler):
        """Weight (case insensitive W): 'W70.3' populates correctly"""
        quick_capture_instance.process("W70.3")
        mock_vault_handler.populate_weight_tag.assert_called_once_with("70.3")

    def test_weight_case_insensitive_uppercase_weight(self, quick_capture_instance, mock_vault_handler):
        """Weight (case insensitive WEIGHT): 'WEIGHT 70.3' populates correctly"""
        quick_capture_instance.process("WEIGHT 70.3")
        mock_vault_handler.populate_weight_tag.assert_called_once_with("70.3")

    def test_weight_case_insensitive_mixed_weight(self, quick_capture_instance, mock_vault_handler):
        """Weight (case insensitive Weight): 'Weight 70.3' populates correctly"""
        quick_capture_instance.process("Weight 70.3")
        mock_vault_handler.populate_weight_tag.assert_called_once_with("70.3")

    def test_weight_with_leading_whitespace(self, quick_capture_instance, mock_vault_handler):
        """Weight (leading whitespace): '  w70.3' populates correctly"""
        quick_capture_instance.process("  w70.3")
        mock_vault_handler.populate_weight_tag.assert_called_once_with("70.3")

    def test_weight_with_trailing_whitespace(self, quick_capture_instance, mock_vault_handler):
        """Weight (trailing whitespace): 'w70.3  ' populates correctly"""
        quick_capture_instance.process("w70.3  ")
        mock_vault_handler.populate_weight_tag.assert_called_once_with("70.3")

    def test_weight_with_both_whitespace(self, quick_capture_instance, mock_vault_handler):
        """Weight (both whitespace): '  w70.3  ' populates correctly"""
        quick_capture_instance.process("  w70.3  ")
        mock_vault_handler.populate_weight_tag.assert_called_once_with("70.3")

    def test_weight_single_digit_integer(self, quick_capture_instance, mock_vault_handler):
        """Weight (single digit): 'w5' populates [weight::5.0]"""
        quick_capture_instance.process("w5")
        mock_vault_handler.populate_weight_tag.assert_called_once_with("5.0")

    def test_weight_three_digit_integer(self, quick_capture_instance, mock_vault_handler):
        """Weight (three digits): 'w150' populates [weight::150.0]"""
        quick_capture_instance.process("w150")
        mock_vault_handler.populate_weight_tag.assert_called_once_with("150.0")

    def test_weight_with_leading_zero_decimal(self, quick_capture_instance, mock_vault_handler):
        """Weight (leading zero decimal): 'w70.0' populates [weight::70.0]"""
        quick_capture_instance.process("w70.0")
        mock_vault_handler.populate_weight_tag.assert_called_once_with("70.0")

    def test_weight_zero_value(self, quick_capture_instance, mock_vault_handler):
        """Weight (zero value): 'w0' populates [weight::0.0]"""
        quick_capture_instance.process("w0")
        mock_vault_handler.populate_weight_tag.assert_called_once_with("0.0")

    def test_weight_does_not_match_random_w(self, quick_capture_instance, mock_vault_handler):
        """Weight (no match - random w): 'w' alone should go to fallback"""
        quick_capture_instance.process("w")
        mock_vault_handler.append_to_daily_note.assert_called_once_with("w")
        assert not mock_vault_handler.populate_weight_tag.called

    def test_weight_does_not_match_w_with_text(self, quick_capture_instance, mock_vault_handler):
        """Weight (no match - w with text): 'w hello' should go to fallback"""
        quick_capture_instance.process("w hello")
        mock_vault_handler.append_to_daily_note.assert_called_once_with("w hello")
        assert not mock_vault_handler.populate_weight_tag.called

    def test_weight_does_not_match_weight_alone(self, quick_capture_instance, mock_vault_handler):
        """Weight (no match - weight alone): 'weight' alone should go to fallback"""
        quick_capture_instance.process("weight")
        mock_vault_handler.append_to_daily_note.assert_called_once_with("weight")
        assert not mock_vault_handler.populate_weight_tag.called

    def test_weight_with_multiple_spaces_between(self, quick_capture_instance, mock_vault_handler):
        """Weight (multiple spaces): 'weight   70.3' populates correctly"""
        quick_capture_instance.process("weight   70.3")
        mock_vault_handler.populate_weight_tag.assert_called_once_with("70.3")

    def test_weight_rounding_up(self, quick_capture_instance, mock_vault_handler):
        """Weight (rounding up): 'w70.36' rounds to [weight::70.4]"""
        quick_capture_instance.process("w70.36")
        mock_vault_handler.populate_weight_tag.assert_called_once_with("70.4")

    def test_weight_rounding_down(self, quick_capture_instance, mock_vault_handler):
        """Weight (rounding down): 'w70.34' rounds to [weight::70.3]"""
        quick_capture_instance.process("w70.34")
        mock_vault_handler.populate_weight_tag.assert_called_once_with("70.3")

    def test_weight_rounding_exactly_half(self, quick_capture_instance, mock_vault_handler):
        """Weight (rounding half): 'w70.35' rounds to [weight::70.4] (round half up)"""
        quick_capture_instance.process("w70.35")
        mock_vault_handler.populate_weight_tag.assert_called_once_with("70.4")
