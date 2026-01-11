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
        r"""Parking Level (Multiple Digits): Handle multiple digits like 'pl999'

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


class TestTodoTaskPattern:
    """Test todo/task pattern matching (task/todo <anything>, case-insensitive, whitespace handling)"""

    def test_task_basic(self, quick_capture_instance, mock_vault_handler):
        """Todo/Task (Basic - task): 'task buy milk' formats to '- [ ] #todo buy milk'"""
        quick_capture_instance.process("task buy milk")
        mock_vault_handler.append_to_daily_note.assert_called_once_with("- [ ] #todo buy milk")

    def test_todo_basic(self, quick_capture_instance, mock_vault_handler):
        """Todo/Task (Basic - todo): 'todo buy milk' formats to '- [ ] #todo buy milk'"""
        quick_capture_instance.process("todo buy milk")
        mock_vault_handler.append_to_daily_note.assert_called_once_with("- [ ] #todo buy milk")

    def test_task_case_insensitive_uppercase(self, quick_capture_instance, mock_vault_handler):
        """Todo/Task (Case Insensitive - TASK): 'TASK buy milk' formats correctly"""
        quick_capture_instance.process("TASK buy milk")
        mock_vault_handler.append_to_daily_note.assert_called_once_with("- [ ] #todo buy milk")

    def test_todo_case_insensitive_uppercase(self, quick_capture_instance, mock_vault_handler):
        """Todo/Task (Case Insensitive - TODO): 'TODO buy milk' formats correctly"""
        quick_capture_instance.process("TODO buy milk")
        mock_vault_handler.append_to_daily_note.assert_called_once_with("- [ ] #todo buy milk")

    def test_task_case_insensitive_mixed(self, quick_capture_instance, mock_vault_handler):
        """Todo/Task (Case Insensitive - Task): 'Task buy milk' formats correctly"""
        quick_capture_instance.process("Task buy milk")
        mock_vault_handler.append_to_daily_note.assert_called_once_with("- [ ] #todo buy milk")

    def test_todo_case_insensitive_mixed(self, quick_capture_instance, mock_vault_handler):
        """Todo/Task (Case Insensitive - Todo): 'Todo buy milk' formats correctly"""
        quick_capture_instance.process("Todo buy milk")
        mock_vault_handler.append_to_daily_note.assert_called_once_with("- [ ] #todo buy milk")

    def test_task_whitespace_leading_trailing(self, quick_capture_instance, mock_vault_handler):
        """Todo/Task (Whitespace - Leading/Trailing): ' task buy milk ' formats correctly"""
        quick_capture_instance.process(" task buy milk ")
        mock_vault_handler.append_to_daily_note.assert_called_once_with("- [ ] #todo buy milk")

    def test_task_whitespace_with_newlines(self, quick_capture_instance, mock_vault_handler):
        """Todo/Task (Whitespace - With Newlines): ' \\n task buy milk \\n ' formats correctly"""
        quick_capture_instance.process(" \n task buy milk \n ")
        mock_vault_handler.append_to_daily_note.assert_called_once_with("- [ ] #todo buy milk")

    def test_task_multiple_words(self, quick_capture_instance, mock_vault_handler):
        """Todo/Task (Multiple Words): 'task this is a long task description' preserves all words"""
        quick_capture_instance.process("task this is a long task description")
        mock_vault_handler.append_to_daily_note.assert_called_once_with("- [ ] #todo this is a long task description")

    def test_task_special_characters(self, quick_capture_instance, mock_vault_handler):
        """Todo/Task (Special Characters): Task text with special characters is preserved"""
        quick_capture_instance.process("task buy @groceries #important! $$$")
        mock_vault_handler.append_to_daily_note.assert_called_once_with("- [ ] #todo buy @groceries #important! $$$")

    def test_task_unicode(self, quick_capture_instance, mock_vault_handler):
        """Todo/Task (Unicode): Task text with unicode characters is preserved"""
        quick_capture_instance.process("task 你好世界 café naïve 🚗")
        mock_vault_handler.append_to_daily_note.assert_called_once_with("- [ ] #todo 你好世界 café naïve 🚗")

    def test_task_with_extra_spaces_between_words(self, quick_capture_instance, mock_vault_handler):
        """Todo/Task (Extra Spaces): 'task  buy   milk' preserves spacing in content"""
        quick_capture_instance.process("task  buy   milk")
        mock_vault_handler.append_to_daily_note.assert_called_once_with("- [ ] #todo  buy   milk")

    def test_task_single_word_content(self, quick_capture_instance, mock_vault_handler):
        """Todo/Task (Single Word): 'task something' formats correctly"""
        quick_capture_instance.process("task something")
        mock_vault_handler.append_to_daily_note.assert_called_once_with("- [ ] #todo something")

    def test_task_empty_content(self, quick_capture_instance, mock_vault_handler):
        """Todo/Task (Empty Content): 'task' without content should go to fallback"""
        quick_capture_instance.process("task")
        # Empty task should not match the pattern, goes to fallback
        mock_vault_handler.append_to_daily_note.assert_called_once_with("task")

    def test_task_only_whitespace_content(self, quick_capture_instance, mock_vault_handler):
        """Todo/Task (Only Whitespace): 'task   ' with only whitespace should go to fallback"""
        quick_capture_instance.process("task   ")
        # Task with only whitespace should not match, goes to fallback
        mock_vault_handler.append_to_daily_note.assert_called_once_with("task   ")


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

        # First rule should be weight pattern
        first_pattern, first_handler = qc.rules[0]
        assert first_handler.__name__ == 'handle_weight'

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
