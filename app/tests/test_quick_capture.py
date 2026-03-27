"""Tests for QuickCapture rule matching and text processing"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime


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
        mock_vault_handler.append_to_daily_note.assert_called_once_with("[ ] #todo buy milk")

    def test_todo_basic(self, quick_capture_instance, mock_vault_handler):
        """Todo/Task (Basic - todo): 'todo buy milk' formats to '- [ ] #todo buy milk'"""
        quick_capture_instance.process("todo buy milk")
        mock_vault_handler.append_to_daily_note.assert_called_once_with("[ ] #todo buy milk")

    def test_task_case_insensitive_uppercase(self, quick_capture_instance, mock_vault_handler):
        """Todo/Task (Case Insensitive - TASK): 'TASK buy milk' formats correctly"""
        quick_capture_instance.process("TASK buy milk")
        mock_vault_handler.append_to_daily_note.assert_called_once_with("[ ] #todo buy milk")

    def test_todo_case_insensitive_uppercase(self, quick_capture_instance, mock_vault_handler):
        """Todo/Task (Case Insensitive - TODO): 'TODO buy milk' formats correctly"""
        quick_capture_instance.process("TODO buy milk")
        mock_vault_handler.append_to_daily_note.assert_called_once_with("[ ] #todo buy milk")

    def test_task_case_insensitive_mixed(self, quick_capture_instance, mock_vault_handler):
        """Todo/Task (Case Insensitive - Task): 'Task buy milk' formats correctly"""
        quick_capture_instance.process("Task buy milk")
        mock_vault_handler.append_to_daily_note.assert_called_once_with("[ ] #todo buy milk")

    def test_todo_case_insensitive_mixed(self, quick_capture_instance, mock_vault_handler):
        """Todo/Task (Case Insensitive - Todo): 'Todo buy milk' formats correctly"""
        quick_capture_instance.process("Todo buy milk")
        mock_vault_handler.append_to_daily_note.assert_called_once_with("[ ] #todo buy milk")

    def test_task_whitespace_leading_trailing(self, quick_capture_instance, mock_vault_handler):
        """Todo/Task (Whitespace - Leading/Trailing): ' task buy milk ' formats correctly"""
        quick_capture_instance.process(" task buy milk ")
        mock_vault_handler.append_to_daily_note.assert_called_once_with("[ ] #todo buy milk")

    def test_task_whitespace_with_newlines(self, quick_capture_instance, mock_vault_handler):
        """Todo/Task (Whitespace - With Newlines): ' \\n task buy milk \\n ' formats correctly"""
        quick_capture_instance.process(" \n task buy milk \n ")
        mock_vault_handler.append_to_daily_note.assert_called_once_with("[ ] #todo buy milk")

    def test_task_multiple_words(self, quick_capture_instance, mock_vault_handler):
        """Todo/Task (Multiple Words): 'task this is a long task description' preserves all words"""
        quick_capture_instance.process("task this is a long task description")
        mock_vault_handler.append_to_daily_note.assert_called_once_with("[ ] #todo this is a long task description")

    def test_task_special_characters(self, quick_capture_instance, mock_vault_handler):
        """Todo/Task (Special Characters): Task text with special characters is preserved"""
        quick_capture_instance.process("task buy @groceries #important! $$$")
        mock_vault_handler.append_to_daily_note.assert_called_once_with("[ ] #todo buy @groceries #important! $$$")

    def test_task_unicode(self, quick_capture_instance, mock_vault_handler):
        """Todo/Task (Unicode): Task text with unicode characters is preserved"""
        quick_capture_instance.process("task 你好世界 café naïve 🚗")
        mock_vault_handler.append_to_daily_note.assert_called_once_with("[ ] #todo 你好世界 café naïve 🚗")

    def test_task_with_extra_spaces_between_words(self, quick_capture_instance, mock_vault_handler):
        """Todo/Task (Extra Spaces): 'task  buy   milk' strips separator whitespace, preserves content spacing"""
        quick_capture_instance.process("task  buy   milk")
        mock_vault_handler.append_to_daily_note.assert_called_once_with("[ ] #todo buy   milk")

    def test_task_single_word_content(self, quick_capture_instance, mock_vault_handler):
        """Todo/Task (Single Word): 'task something' formats correctly"""
        quick_capture_instance.process("task something")
        mock_vault_handler.append_to_daily_note.assert_called_once_with("[ ] #todo something")

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

    def test_task_colon_separator(self, quick_capture_instance, mock_vault_handler):
        """Todo/Task (Colon): 'task: buy milk' strips colon separator"""
        quick_capture_instance.process("task: buy milk")
        mock_vault_handler.append_to_daily_note.assert_called_once_with("[ ] #todo buy milk")

    def test_task_colon_with_spaces(self, quick_capture_instance, mock_vault_handler):
        """Todo/Task (Colon With Spaces): 'task : buy milk' strips colon and surrounding spaces"""
        quick_capture_instance.process("task : buy milk")
        mock_vault_handler.append_to_daily_note.assert_called_once_with("[ ] #todo buy milk")

    def test_task_dash_separator(self, quick_capture_instance, mock_vault_handler):
        """Todo/Task (Dash): 'task - buy milk' strips dash separator"""
        quick_capture_instance.process("task - buy milk")
        mock_vault_handler.append_to_daily_note.assert_called_once_with("[ ] #todo buy milk")

    def test_task_emdash_separator(self, quick_capture_instance, mock_vault_handler):
        """Todo/Task (Em Dash): 'task — buy milk' strips em dash separator"""
        quick_capture_instance.process("task — buy milk")
        mock_vault_handler.append_to_daily_note.assert_called_once_with("[ ] #todo buy milk")

    def test_todo_colon_separator(self, quick_capture_instance, mock_vault_handler):
        """Todo/Task (Todo Colon): 'todo: buy milk' strips colon separator"""
        quick_capture_instance.process("todo: buy milk")
        mock_vault_handler.append_to_daily_note.assert_called_once_with("[ ] #todo buy milk")


class TestFoodLogPattern:
    """Test food log/diary pattern matching (food log/food diary <message>, case-insensitive)"""

    def test_food_log_basic(self, quick_capture_instance, mock_vault_handler):
        """Food Log (Basic): 'food log chicken salad' calls append_to_embed_journal"""
        quick_capture_instance.process("food log chicken salad")
        mock_vault_handler.append_to_embed_journal.assert_called_once_with("chicken salad")

    def test_food_diary_basic(self, quick_capture_instance, mock_vault_handler):
        """Food Diary (Basic): 'food diary yogurt parfait' calls append_to_embed_journal"""
        quick_capture_instance.process("food diary yogurt parfait")
        mock_vault_handler.append_to_embed_journal.assert_called_once_with("yogurt parfait")

    def test_food_log_case_insensitive_uppercase(self, quick_capture_instance, mock_vault_handler):
        """Food Log (Case Insensitive - FOOD LOG): 'FOOD LOG eggs' calls handler"""
        quick_capture_instance.process("FOOD LOG eggs")
        mock_vault_handler.append_to_embed_journal.assert_called_once_with("eggs")

    def test_food_diary_case_insensitive_uppercase(self, quick_capture_instance, mock_vault_handler):
        """Food Diary (Case Insensitive - FOOD DIARY): 'FOOD DIARY eggs' calls handler"""
        quick_capture_instance.process("FOOD DIARY eggs")
        mock_vault_handler.append_to_embed_journal.assert_called_once_with("eggs")

    def test_food_log_case_insensitive_mixed(self, quick_capture_instance, mock_vault_handler):
        """Food Log (Case Insensitive - Mixed): 'Food Log banana' calls handler"""
        quick_capture_instance.process("Food Log banana")
        mock_vault_handler.append_to_embed_journal.assert_called_once_with("banana")

    def test_food_diary_case_insensitive_mixed(self, quick_capture_instance, mock_vault_handler):
        """Food Diary (Case Insensitive - Mixed): 'Food Diary banana' calls handler"""
        quick_capture_instance.process("Food Diary banana")
        mock_vault_handler.append_to_embed_journal.assert_called_once_with("banana")

    def test_food_log_leading_whitespace(self, quick_capture_instance, mock_vault_handler):
        """Food Log (Leading Whitespace): '  food log eggs' calls handler"""
        quick_capture_instance.process("  food log eggs")
        mock_vault_handler.append_to_embed_journal.assert_called_once_with("eggs")

    def test_food_log_trailing_whitespace_in_message(self, quick_capture_instance, mock_vault_handler):
        """Food Log (Trailing Whitespace): 'food log eggs  ' strips trailing whitespace"""
        quick_capture_instance.process("food log eggs  ")
        mock_vault_handler.append_to_embed_journal.assert_called_once_with("eggs")

    def test_food_log_multi_word_message(self, quick_capture_instance, mock_vault_handler):
        """Food Log (Multi Word): 'food log grilled chicken with rice and salad' preserves full message"""
        quick_capture_instance.process("food log grilled chicken with rice and salad")
        mock_vault_handler.append_to_embed_journal.assert_called_once_with("grilled chicken with rice and salad")

    def test_food_log_no_message_falls_back(self, quick_capture_instance, mock_vault_handler):
        """Food Log (No Message): 'food log' without content goes to fallback"""
        quick_capture_instance.process("food log")
        mock_vault_handler.append_to_embed_journal.assert_not_called()
        mock_vault_handler.append_to_daily_note.assert_called_once_with("food log")

    def test_food_diary_no_message_falls_back(self, quick_capture_instance, mock_vault_handler):
        """Food Diary (No Message): 'food diary' without content goes to fallback"""
        quick_capture_instance.process("food diary")
        mock_vault_handler.append_to_embed_journal.assert_not_called()
        mock_vault_handler.append_to_daily_note.assert_called_once_with("food diary")

    def test_food_log_only_whitespace_after_falls_back(self, quick_capture_instance, mock_vault_handler):
        """Food Log (Only Whitespace After): 'food log   ' goes to fallback"""
        quick_capture_instance.process("food log   ")
        mock_vault_handler.append_to_embed_journal.assert_not_called()
        mock_vault_handler.append_to_daily_note.assert_called_once_with("food log   ")

    def test_food_does_not_match_alone(self, quick_capture_instance, mock_vault_handler):
        """Food Log (No Partial Match): 'food something' without log/diary keyword goes to fallback"""
        quick_capture_instance.process("food something")
        mock_vault_handler.append_to_embed_journal.assert_not_called()
        mock_vault_handler.append_to_daily_note.assert_called_once_with("food something")

    def test_food_log_does_not_conflict_with_other_rules(self, quick_capture_instance, mock_vault_handler):
        """Food Log (No Conflict): 'pl3' still matches parking level, not food log"""
        quick_capture_instance.process("pl3")
        mock_vault_handler.append_to_embed_journal.assert_not_called()
        mock_vault_handler.append_to_daily_note.assert_called_once_with("Parking Level: 3")

    def test_food_log_colon_separator(self, quick_capture_instance, mock_vault_handler):
        """Food Log (Colon): 'food log: apple' strips colon separator"""
        quick_capture_instance.process("food log: apple")
        mock_vault_handler.append_to_embed_journal.assert_called_once_with("apple")

    def test_food_log_colon_with_spaces(self, quick_capture_instance, mock_vault_handler):
        """Food Log (Colon With Spaces): 'food log : apple' strips colon and surrounding spaces"""
        quick_capture_instance.process("food log : apple")
        mock_vault_handler.append_to_embed_journal.assert_called_once_with("apple")

    def test_food_log_dash_separator(self, quick_capture_instance, mock_vault_handler):
        """Food Log (Dash): 'food log - apple' strips dash separator"""
        quick_capture_instance.process("food log - apple")
        mock_vault_handler.append_to_embed_journal.assert_called_once_with("apple")

    def test_food_log_emdash_separator(self, quick_capture_instance, mock_vault_handler):
        """Food Log (Em Dash): 'food log — apple' strips em dash separator"""
        quick_capture_instance.process("food log — apple")
        mock_vault_handler.append_to_embed_journal.assert_called_once_with("apple")

    def test_food_diary_colon_separator(self, quick_capture_instance, mock_vault_handler):
        """Food Diary (Colon): 'food diary: banana' strips colon separator"""
        quick_capture_instance.process("food diary: banana")
        mock_vault_handler.append_to_embed_journal.assert_called_once_with("banana")


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


class TestVaultIntegration:
    """Test integration between QuickCapture and VaultHandler"""

    def test_task_no_double_dash_in_file(self, test_vault, tmp_path):
        """Task Integration: Task capture should not create double dashes in the file

        Bug: When a task is captured, the handle_todo_task adds "- [ ] #todo" prefix,
        and then append_to_daily_note adds another "- " prefix, resulting in "- - [ ] #todo"
        instead of the expected "- [ ] #todo".
        """
        from vault_handler import VaultHandler
        from quick_capture import QuickCapture
        from datetime import date

        # Create vault handler with test vault
        vault_handler = VaultHandler(str(test_vault))

        # Create quick capture instance
        qc = QuickCapture(vault_handler)

        # Create a daily note for today
        today = date.today()
        daily_note_path = vault_handler.create_daily_note(target_date=today)

        # Process a task
        qc.process("task my important task")

        # Read the file content
        content = daily_note_path.read_text(encoding='utf-8')

        # The file should contain "- [ ] #todo my important task"
        # NOT "- - [ ] #todo my important task"
        assert "- [ ] #todo my important task" in content, \
            f"Expected single dash checkbox, but file content is:\n{content}"

        # Verify there's no double dash
        assert "- - [ ] #todo" not in content, \
            f"Found double dash in file content:\n{content}"


class TestEmbedJournalPattern:
    """Test embed journal pattern matching (embed <message>, case-insensitive, whitespace handling)"""

    def test_embed_basic(self, quick_capture_instance, mock_vault_handler):
        """Embed Journal (Basic): 'embed filter coffee' calls append_to_embed_journal"""
        quick_capture_instance.process("embed filter coffee")
        mock_vault_handler.append_to_embed_journal.assert_called_once_with("filter coffee")

    def test_embed_case_insensitive_uppercase(self, quick_capture_instance, mock_vault_handler):
        """Embed Journal (Case Insensitive - EMBED): 'EMBED test' calls handler"""
        quick_capture_instance.process("EMBED test")
        mock_vault_handler.append_to_embed_journal.assert_called_once_with("test")

    def test_embed_case_insensitive_mixed(self, quick_capture_instance, mock_vault_handler):
        """Embed Journal (Case Insensitive - Embed): 'Embed test' calls handler"""
        quick_capture_instance.process("Embed test")
        mock_vault_handler.append_to_embed_journal.assert_called_once_with("test")

    def test_embed_leading_whitespace(self, quick_capture_instance, mock_vault_handler):
        """Embed Journal (Leading Whitespace): '  embed test' calls handler"""
        quick_capture_instance.process("  embed test")
        mock_vault_handler.append_to_embed_journal.assert_called_once_with("test")

    def test_embed_trailing_whitespace_in_message(self, quick_capture_instance, mock_vault_handler):
        """Embed Journal (Trailing Whitespace): 'embed test  ' strips trailing whitespace"""
        quick_capture_instance.process("embed test  ")
        mock_vault_handler.append_to_embed_journal.assert_called_once_with("test")

    def test_embed_multi_word_message(self, quick_capture_instance, mock_vault_handler):
        """Embed Journal (Multi Word): 'embed filter coffee with milk' preserves full message"""
        quick_capture_instance.process("embed filter coffee with milk")
        mock_vault_handler.append_to_embed_journal.assert_called_once_with("filter coffee with milk")

    def test_embed_message_with_commas(self, quick_capture_instance, mock_vault_handler):
        """Embed Journal (Commas): 'embed getting hungry, waiting for 11' preserves commas"""
        quick_capture_instance.process("embed getting hungry, waiting for 11")
        mock_vault_handler.append_to_embed_journal.assert_called_once_with("getting hungry, waiting for 11")

    def test_embed_no_message_falls_back(self, quick_capture_instance, mock_vault_handler):
        """Embed Journal (No Message): 'embed' without content goes to fallback"""
        quick_capture_instance.process("embed")
        mock_vault_handler.append_to_embed_journal.assert_not_called()
        mock_vault_handler.append_to_daily_note.assert_called_once_with("embed")

    def test_embed_only_whitespace_after_falls_back(self, quick_capture_instance, mock_vault_handler):
        """Embed Journal (Only Whitespace After): 'embed   ' goes to fallback"""
        quick_capture_instance.process("embed   ")
        mock_vault_handler.append_to_embed_journal.assert_not_called()
        mock_vault_handler.append_to_daily_note.assert_called_once_with("embed   ")

    def test_embedded_does_not_match(self, quick_capture_instance, mock_vault_handler):
        """Embed Journal (No Partial Match): 'embedded something' does not trigger embed rule"""
        quick_capture_instance.process("embedded something")
        mock_vault_handler.append_to_embed_journal.assert_not_called()
        mock_vault_handler.append_to_daily_note.assert_called_once_with("embedded something")

    def test_embed_special_characters(self, quick_capture_instance, mock_vault_handler):
        """Embed Journal (Special Characters): Message with special chars is preserved"""
        quick_capture_instance.process("embed test @#$%^&*()")
        mock_vault_handler.append_to_embed_journal.assert_called_once_with("test @#$%^&*()")

    def test_embed_does_not_conflict_with_other_rules(self, quick_capture_instance, mock_vault_handler):
        """Embed Journal (No Conflict): 'pl3' still matches parking level, not embed"""
        quick_capture_instance.process("pl3")
        mock_vault_handler.append_to_embed_journal.assert_not_called()
        mock_vault_handler.append_to_daily_note.assert_called_once_with("Parking Level: 3")

    def test_embed_colon_separator(self, quick_capture_instance, mock_vault_handler):
        """Embed Journal (Colon): 'embed: filter coffee' strips colon separator"""
        quick_capture_instance.process("embed: filter coffee")
        mock_vault_handler.append_to_embed_journal.assert_called_once_with("filter coffee")

    def test_embed_colon_with_spaces(self, quick_capture_instance, mock_vault_handler):
        """Embed Journal (Colon With Spaces): 'embed : filter coffee' strips colon and surrounding spaces"""
        quick_capture_instance.process("embed : filter coffee")
        mock_vault_handler.append_to_embed_journal.assert_called_once_with("filter coffee")

    def test_embed_dash_separator(self, quick_capture_instance, mock_vault_handler):
        """Embed Journal (Dash): 'embed - filter coffee' strips dash separator"""
        quick_capture_instance.process("embed - filter coffee")
        mock_vault_handler.append_to_embed_journal.assert_called_once_with("filter coffee")

    def test_embed_emdash_separator(self, quick_capture_instance, mock_vault_handler):
        """Embed Journal (Em Dash): 'embed — filter coffee' strips em dash separator"""
        quick_capture_instance.process("embed — filter coffee")
        mock_vault_handler.append_to_embed_journal.assert_called_once_with("filter coffee")
