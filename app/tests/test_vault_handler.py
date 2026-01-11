"""Tests for VaultHandler daily note creation functionality"""

import pytest
from datetime import date
from pathlib import Path
from vault_handler import VaultHandler


class TestTemplaterProcessing:
    """Tests for Templater variable processing"""

    def test_process_templater_variables_basic(self, test_vault):
        """Process Templater variables for a normal date"""
        handler = VaultHandler(str(test_vault))
        test_date = date(2025, 1, 15)

        # Read template content
        template_content = handler.template_path.read_text(encoding='utf-8')

        # Process Templater variables
        processed = handler._process_templater_variables(template_content, test_date)

        # Verify yesterday link
        assert "2025-01-14" in processed
        # Verify tomorrow link
        assert "2025-01-16" in processed
        # Verify current date
        assert "2025-01-15" in processed
        # Verify no Templater tags remain
        assert "<%" not in processed
        assert "%>" not in processed
        # Verify frontmatter preserved
        assert "tags:" in processed
        assert "daily_note" in processed

    def test_process_templater_variables_year_boundary(self, test_vault):
        """Handle year boundary correctly (Dec 31 -> Jan 1)"""
        handler = VaultHandler(str(test_vault))

        # Test New Year's Eve
        nye_date = date(2024, 12, 31)
        template_content = handler.template_path.read_text(encoding='utf-8')
        processed = handler._process_templater_variables(template_content, nye_date)

        assert "2024-12-30" in processed  # Yesterday
        assert "2025-01-01" in processed  # Tomorrow (crosses year boundary)
        assert "2024-12-31" in processed  # Current

        # Test New Year's Day
        nyd_date = date(2025, 1, 1)
        processed = handler._process_templater_variables(template_content, nyd_date)

        assert "2024-12-31" in processed  # Yesterday (crosses year boundary)
        assert "2025-01-02" in processed  # Tomorrow
        assert "2025-01-01" in processed  # Current

    def test_process_templater_variables_leap_year(self, test_vault):
        """Handle leap year dates correctly"""
        handler = VaultHandler(str(test_vault))
        template_content = handler.template_path.read_text(encoding='utf-8')

        # Test Feb 29 in leap year (2024)
        leap_day = date(2024, 2, 29)
        processed = handler._process_templater_variables(template_content, leap_day)

        assert "2024-02-28" in processed  # Yesterday
        assert "2024-03-01" in processed  # Tomorrow
        assert "2024-02-29" in processed  # Current

        # Test Feb 28 in non-leap year (2025)
        feb28 = date(2025, 2, 28)
        processed = handler._process_templater_variables(template_content, feb28)

        assert "2025-02-27" in processed  # Yesterday
        assert "2025-03-01" in processed  # Tomorrow
        assert "2025-02-28" in processed  # Current

    def test_process_templater_variables_whitespace(self, test_vault):
        """Handle Templater tags with various whitespace"""
        handler = VaultHandler(str(test_vault))
        test_date = date(2025, 6, 15)

        # Test with extra whitespace in tags
        template_with_spaces = """
<%  fileDate  =  moment(tp.file.title,  'YYYY-MM-DD').subtract(1,  'd').format('YYYY-MM-DD')  %>
<%fileDate=moment(tp.file.title,'YYYY-MM-DD').add(1,'d').format('YYYY-MM-DD')%>
<%   tp.date.now()   %>
"""
        processed = handler._process_templater_variables(template_with_spaces, test_date)

        assert "2025-06-14" in processed  # Yesterday
        assert "2025-06-16" in processed  # Tomorrow
        assert "2025-06-15" in processed  # Current
        assert "<%" not in processed


class TestDailyNoteCreation:
    """Tests for daily note creation"""

    def test_create_daily_note_success(self, test_vault):
        """Successfully create daily note with processed Templater variables"""
        handler = VaultHandler(str(test_vault))
        test_date = date(2025, 1, 15)

        note_path = handler.create_daily_note(target_date=test_date)

        assert note_path.exists()
        assert note_path.name == "2025-01-15.md"
        assert note_path.parent.name == "Daily Notes"

        content = note_path.read_text(encoding='utf-8')
        assert "2025-01-14" in content  # Yesterday
        assert "2025-01-16" in content  # Tomorrow
        assert "2025-01-15" in content  # Current date
        assert "<%" not in content      # No Templater tags remain
        assert "tags:" in content       # Frontmatter preserved
        assert "daily_note" in content
        assert "## Quick Capture" in content  # Sections preserved

    def test_create_daily_note_default_date(self, test_vault):
        """Create note using today's date when date not provided"""
        handler = VaultHandler(str(test_vault))

        note_path = handler.create_daily_note()

        assert note_path.exists()
        today = date.today()
        expected_filename = today.strftime('%Y-%m-%d') + '.md'
        assert note_path.name == expected_filename

        content = note_path.read_text(encoding='utf-8')
        assert today.strftime('%Y-%m-%d') in content

    def test_create_daily_note_custom_date(self, test_vault):
        """Accept and use custom date parameter"""
        handler = VaultHandler(str(test_vault))
        custom_date = date(2023, 7, 4)

        note_path = handler.create_daily_note(target_date=custom_date)

        assert note_path.exists()
        assert note_path.name == "2023-07-04.md"

        content = note_path.read_text(encoding='utf-8')
        assert "2023-07-03" in content  # Yesterday
        assert "2023-07-05" in content  # Tomorrow
        assert "2023-07-04" in content  # Current

    def test_create_daily_note_exists_error(self, test_vault):
        """Raise FileExistsError when note exists and exist_ok=False"""
        handler = VaultHandler(str(test_vault))
        test_date = date(2025, 1, 15)

        # Create note first time
        handler.create_daily_note(target_date=test_date)

        # Second attempt should raise error
        with pytest.raises(FileExistsError) as exc_info:
            handler.create_daily_note(target_date=test_date, exist_ok=False)

        assert "already exists" in str(exc_info.value)
        assert "2025-01-15.md" in str(exc_info.value)

    def test_create_daily_note_exists_ok(self, test_vault):
        """Return existing note path when exist_ok=True"""
        handler = VaultHandler(str(test_vault))
        test_date = date(2025, 1, 15)

        # Create note first time
        first_path = handler.create_daily_note(target_date=test_date)
        original_content = first_path.read_text(encoding='utf-8')

        # Second attempt with exist_ok=True should succeed
        second_path = handler.create_daily_note(target_date=test_date, exist_ok=True)

        assert second_path == first_path
        assert second_path.exists()
        # Content should be unchanged
        assert second_path.read_text(encoding='utf-8') == original_content

    def test_create_daily_note_template_missing(self, test_vault):
        """Raise FileNotFoundError when template doesn't exist"""
        handler = VaultHandler(str(test_vault))
        test_date = date(2025, 1, 15)

        # Delete template
        handler.template_path.unlink()

        # Attempt to create note
        with pytest.raises(FileNotFoundError) as exc_info:
            handler.create_daily_note(target_date=test_date)

        assert "Template not found" in str(exc_info.value)
        assert str(handler.template_path) in str(exc_info.value)

    def test_create_daily_note_creates_folder(self, test_vault):
        """Create Daily Notes folder if it doesn't exist"""
        handler = VaultHandler(str(test_vault))
        test_date = date(2025, 1, 15)

        # Ensure Daily Notes folder doesn't exist
        assert not handler.daily_notes_folder.exists()

        # Create note
        note_path = handler.create_daily_note(target_date=test_date)

        # Verify folder was created
        assert handler.daily_notes_folder.exists()
        assert handler.daily_notes_folder.is_dir()
        assert note_path.exists()
        assert note_path.parent == handler.daily_notes_folder

    def test_create_daily_note_utf8_encoding(self, test_vault):
        """Handle UTF-8 characters correctly (一 Obsidian 一)"""
        handler = VaultHandler(str(test_vault))
        test_date = date(2025, 1, 15)

        # Verify template path contains unicode
        assert "一 Obsidian 一" in str(handler.template_path)
        assert handler.template_path.exists()

        # Create note
        note_path = handler.create_daily_note(target_date=test_date)

        # Verify content is properly encoded
        content = note_path.read_text(encoding='utf-8')
        assert isinstance(content, str)
        # Verify emoji and unicode are preserved
        assert "🛫" in content


class TestAppendToDailyNote:
    """Tests for append_to_daily_note functionality (TDD - tests written first)"""

    # Core Functionality Tests

    def test_append_first_capture_replaces_placeholder(self, test_vault):
        """First capture: Replace '- ' placeholder with '- <text>'"""
        handler = VaultHandler(str(test_vault))
        test_date = date(2025, 1, 15)

        # Create daily note from template (with '- ' placeholder)
        note_path = handler.create_daily_note(target_date=test_date)

        # Verify placeholder exists (could be "-\n" or "- \n" depending on template)
        content_before = note_path.read_text(encoding='utf-8')
        assert "## Quick Capture" in content_before
        assert ("-\n" in content_before or "- \n" in content_before)

        # Append first capture
        handler.append_to_daily_note("First capture", target_date=test_date)

        # Verify placeholder replaced with actual text
        content_after = note_path.read_text(encoding='utf-8')
        assert "- First capture" in content_after

        # Verify standalone placeholder no longer exists in Quick Capture section
        # Extract Quick Capture section
        qc_start = content_after.find("## Quick Capture")
        qc_end = content_after.find("---", qc_start)
        qc_section = content_after[qc_start:qc_end]

        # Should not have standalone '- ' in Quick Capture section
        assert not (qc_section.count("- \n") > 0 or qc_section.endswith("- "))

        # Verify structure intact
        assert "## Quick Capture" in content_after
        assert "---" in content_after

    def test_append_second_capture_inserts_at_top(self, test_vault):
        """Second capture: Insert new item at top of list (newest first)"""
        handler = VaultHandler(str(test_vault))
        test_date = date(2025, 1, 15)

        # Create daily note and add first capture
        note_path = handler.create_daily_note(target_date=test_date)
        handler.append_to_daily_note("First capture", target_date=test_date)

        # Add second capture
        handler.append_to_daily_note("Second capture", target_date=test_date)

        # Verify order: newest first
        content = note_path.read_text(encoding='utf-8')

        # Extract Quick Capture section
        qc_start = content.find("## Quick Capture")
        qc_end = content.find("---", qc_start)
        qc_section = content[qc_start:qc_end]

        # Verify both items present
        assert "- Second capture" in qc_section
        assert "- First capture" in qc_section

        # Verify order (Second should appear before First)
        second_pos = qc_section.find("- Second capture")
        first_pos = qc_section.find("- First capture")
        assert second_pos < first_pos, "Second capture should appear before First capture (newest first)"

    def test_append_multiple_captures_newest_first(self, test_vault):
        """Multiple captures: Each new capture appears at the top"""
        handler = VaultHandler(str(test_vault))
        test_date = date(2025, 1, 15)

        # Create note and add multiple captures
        note_path = handler.create_daily_note(target_date=test_date)
        handler.append_to_daily_note("First", target_date=test_date)
        handler.append_to_daily_note("Second", target_date=test_date)
        handler.append_to_daily_note("Third", target_date=test_date)
        handler.append_to_daily_note("Fourth", target_date=test_date)
        handler.append_to_daily_note("Fifth", target_date=test_date)

        # Verify order
        content = note_path.read_text(encoding='utf-8')
        qc_start = content.find("## Quick Capture")
        qc_end = content.find("---", qc_start)
        qc_section = content[qc_start:qc_end]

        # All items present
        assert "- First" in qc_section
        assert "- Second" in qc_section
        assert "- Third" in qc_section
        assert "- Fourth" in qc_section
        assert "- Fifth" in qc_section

        # Verify order: Fifth, Fourth, Third, Second, First
        fifth_pos = qc_section.find("- Fifth")
        fourth_pos = qc_section.find("- Fourth")
        third_pos = qc_section.find("- Third")
        second_pos = qc_section.find("- Second")
        first_pos = qc_section.find("- First")

        assert fifth_pos < fourth_pos < third_pos < second_pos < first_pos

    # Error Handling Tests

    def test_append_missing_section_logs_error_and_skips(self, test_vault, caplog):
        """Missing section: Log error and skip modification"""
        handler = VaultHandler(str(test_vault))
        test_date = date(2025, 1, 15)

        # Create daily note
        note_path = handler.create_daily_note(target_date=test_date)

        # Remove Quick Capture section manually
        content = note_path.read_text(encoding='utf-8')
        # Remove everything from "## Quick Capture" to the next section
        qc_start = content.find("## Quick Capture")
        qc_end = content.find("## Trackers")
        modified_content = content[:qc_start] + content[qc_end:]
        note_path.write_text(modified_content, encoding='utf-8')

        # Store original content
        original_content = note_path.read_text(encoding='utf-8')

        # Attempt to append
        handler.append_to_daily_note("Test text", target_date=test_date)

        # Verify error logged
        assert "Quick Capture section not found" in caplog.text

        # Verify file unchanged
        current_content = note_path.read_text(encoding='utf-8')
        assert current_content == original_content

        # Verify no exception raised (graceful failure)
        # If we got here, no exception was raised

    def test_append_empty_section_inserts_first_item(self, test_vault):
        """Empty section: Insert first item when section exists but has no '- ' placeholder"""
        handler = VaultHandler(str(test_vault))
        test_date = date(2025, 1, 15)

        # Create daily note
        note_path = handler.create_daily_note(target_date=test_date)

        # Manually create empty section (no placeholder)
        content = note_path.read_text(encoding='utf-8')
        # Replace placeholder with empty section (handle both "-\n" and "- \n")
        content = content.replace("## Quick Capture\n-\n\n---", "## Quick Capture\n---")
        content = content.replace("## Quick Capture\n- \n\n---", "## Quick Capture\n---")
        note_path.write_text(content, encoding='utf-8')

        # Verify section is empty
        assert "## Quick Capture\n---" in note_path.read_text(encoding='utf-8')

        # Append first item
        handler.append_to_daily_note("First item", target_date=test_date)

        # Verify item inserted
        content_after = note_path.read_text(encoding='utf-8')
        qc_start = content_after.find("## Quick Capture")
        qc_end = content_after.find("---", qc_start)
        qc_section = content_after[qc_start:qc_end]

        assert "- First item" in qc_section

    def test_append_missing_separator(self, test_vault):
        """Missing separator: Handle when '---' separator is missing"""
        handler = VaultHandler(str(test_vault))
        test_date = date(2025, 1, 15)

        # Create daily note
        note_path = handler.create_daily_note(target_date=test_date)

        # Remove separator after Quick Capture
        content = note_path.read_text(encoding='utf-8')
        # Find and remove the first --- after Quick Capture
        qc_start = content.find("## Quick Capture")
        separator_pos = content.find("---", qc_start)
        next_separator_pos = content.find("---", separator_pos + 3)
        # Remove the first --- (keep the placeholder but remove separator)
        content = content[:separator_pos] + content[separator_pos+4:next_separator_pos] + content[next_separator_pos:]
        note_path.write_text(content, encoding='utf-8')

        # Append text
        handler.append_to_daily_note("Test text", target_date=test_date)

        # Verify it worked (found next ## heading as boundary)
        content_after = note_path.read_text(encoding='utf-8')
        qc_start = content_after.find("## Quick Capture")
        next_heading = content_after.find("##", qc_start + 1)
        qc_section = content_after[qc_start:next_heading]

        assert "- Test text" in qc_section

    # Robustness Tests

    def test_append_preserves_other_sections(self, test_vault):
        """Other sections: Modifications only in Quick Capture section"""
        handler = VaultHandler(str(test_vault))
        test_date = date(2025, 1, 15)

        # Create daily note
        note_path = handler.create_daily_note(target_date=test_date)
        original_content = note_path.read_text(encoding='utf-8')

        # Extract sections other than Quick Capture
        frontmatter_end = original_content.find("---", 3)  # Find second ---
        frontmatter = original_content[:frontmatter_end+3]

        trackers_start = original_content.find("## Trackers")
        trackers_section = original_content[trackers_start:]

        # Append to Quick Capture
        handler.append_to_daily_note("Test capture", target_date=test_date)

        # Verify other sections unchanged
        new_content = note_path.read_text(encoding='utf-8')

        # Frontmatter should be identical
        new_frontmatter = new_content[:frontmatter_end+3]
        assert new_frontmatter == frontmatter

        # Trackers section should be identical
        new_trackers_start = new_content.find("## Trackers")
        new_trackers_section = new_content[new_trackers_start:]
        assert new_trackers_section == trackers_section

    def test_append_special_characters(self, test_vault):
        """Special chars: Handle markdown special characters correctly"""
        handler = VaultHandler(str(test_vault))
        test_date = date(2025, 1, 15)

        # Create daily note
        note_path = handler.create_daily_note(target_date=test_date)

        # Append text with special markdown characters
        special_text = "Test #tag [[link]] - bullet *italic* **bold**"
        handler.append_to_daily_note(special_text, target_date=test_date)

        # Verify text preserved exactly
        content = note_path.read_text(encoding='utf-8')
        assert special_text in content

    def test_append_unicode_and_emoji(self, test_vault):
        """Unicode: Handle unicode and emoji correctly"""
        handler = VaultHandler(str(test_vault))
        test_date = date(2025, 1, 15)

        # Create daily note
        note_path = handler.create_daily_note(target_date=test_date)

        # Append text with unicode and emoji
        unicode_text = "Parking 🚗 Level 中文测试"
        handler.append_to_daily_note(unicode_text, target_date=test_date)

        # Verify text preserved with correct encoding
        content = note_path.read_text(encoding='utf-8')
        assert unicode_text in content
        assert isinstance(content, str)

    def test_append_whitespace_placeholder_variations(self, test_vault):
        """Whitespace: Handle '- ', '-  ', '-\\t', etc."""
        handler = VaultHandler(str(test_vault))
        test_date = date(2025, 1, 15)

        # Test with extra spaces
        note_path = handler.create_daily_note(target_date=test_date)
        content = note_path.read_text(encoding='utf-8')
        # Replace '- ' with '-  ' (two spaces)
        content = content.replace("## Quick Capture\n- \n", "## Quick Capture\n-  \n")
        note_path.write_text(content, encoding='utf-8')

        handler.append_to_daily_note("Test", target_date=test_date)

        content_after = note_path.read_text(encoding='utf-8')
        assert "- Test" in content_after

        # Test with tab
        test_date2 = date(2025, 1, 16)
        note_path2 = handler.daily_notes_folder / "2025-01-16.md"
        handler.create_daily_note(target_date=test_date2)
        content2 = note_path2.read_text(encoding='utf-8')
        content2 = content2.replace("## Quick Capture\n- \n", "## Quick Capture\n-\t\n")
        note_path2.write_text(content2, encoding='utf-8')

        handler.append_to_daily_note("Test2", target_date=test_date2)

        content2_after = note_path2.read_text(encoding='utf-8')
        # Should handle tab variation
        assert "- Test2" in content2_after or "Test2" in content2_after


class TestIntegration:
    """Integration tests for append_to_daily_note"""

    def test_append_creates_note(self, test_vault):
        """append_to_daily_note creates note if it doesn't exist"""
        handler = VaultHandler(str(test_vault))

        # Ensure no daily note exists
        today = date.today()
        expected_path = handler.daily_notes_folder / f"{today.strftime('%Y-%m-%d')}.md"
        assert not expected_path.exists()

        # Call append (which should create the note)
        handler.append_to_daily_note("Test text", target_date=today)

        # Verify note was created
        assert expected_path.exists()

        content = expected_path.read_text(encoding='utf-8')
        # Verify it's a properly processed daily note
        assert "tags:" in content
        assert "daily_note" in content
        assert "<%" not in content  # Templater variables processed

    def test_append_uses_existing_note(self, test_vault):
        """append_to_daily_note works with existing note"""
        handler = VaultHandler(str(test_vault))
        today = date.today()

        # Create note first
        note_path = handler.create_daily_note(target_date=today)
        original_content = note_path.read_text(encoding='utf-8')

        # Call append on existing note
        handler.append_to_daily_note("Test text", target_date=today)

        # Verify note still exists and text was appended
        assert note_path.exists()
        current_content = note_path.read_text(encoding='utf-8')
        # Content should now contain the appended text
        assert "Test text" in current_content

    def test_integration_first_capture_full_flow(self, test_vault):
        """E2E: Full flow from QuickCapture.process() to file modification"""
        from quick_capture import QuickCapture

        handler = VaultHandler(str(test_vault))
        quick_capture = QuickCapture(handler)
        test_date = date.today()

        # Process parking level capture (should transform "pl3" → "Parking Level: 3")
        quick_capture.process("pl3")

        # Verify daily note created and contains transformed text
        note_path = handler.daily_notes_folder / f"{test_date.strftime('%Y-%m-%d')}.md"
        assert note_path.exists()

        content = note_path.read_text(encoding='utf-8')
        # Verify transformed text appears (not just "pl3")
        assert "Parking Level: 3" in content

        # Verify it's in the Quick Capture section
        qc_start = content.find("## Quick Capture")
        qc_end = content.find("---", qc_start)
        qc_section = content[qc_start:qc_end]
        assert "- Parking Level: 3" in qc_section

    def test_integration_multiple_captures_full_flow(self, test_vault):
        """E2E: Multiple captures from API maintain order"""
        from quick_capture import QuickCapture

        handler = VaultHandler(str(test_vault))
        quick_capture = QuickCapture(handler)
        test_date = date.today()

        # Process multiple captures with different patterns
        quick_capture.process("pl3")      # Parking level pattern
        quick_capture.process("Buy milk") # Fallback handler
        quick_capture.process("pl5")      # Parking level pattern

        # Verify all captured correctly
        note_path = handler.daily_notes_folder / f"{test_date.strftime('%Y-%m-%d')}.md"
        content = note_path.read_text(encoding='utf-8')

        # Extract Quick Capture section
        qc_start = content.find("## Quick Capture")
        qc_end = content.find("---", qc_start)
        qc_section = content[qc_start:qc_end]

        # Verify all three items present
        assert "Parking Level: 5" in qc_section
        assert "Buy milk" in qc_section
        assert "Parking Level: 3" in qc_section

        # Verify order: newest first (pl5, Buy milk, pl3)
        pl5_pos = qc_section.find("Parking Level: 5")
        milk_pos = qc_section.find("Buy milk")
        pl3_pos = qc_section.find("Parking Level: 3")

        assert pl5_pos < milk_pos < pl3_pos, "Order should be: pl5, Buy milk, pl3 (newest first)"


class TestQuickCaptureEdgeCases:
    """Edge case tests for quick capture functionality"""

    def test_append_empty_string(self, test_vault):
        """Edge case: Handle empty string input"""
        handler = VaultHandler(str(test_vault))
        test_date = date(2025, 1, 15)

        # Create daily note
        note_path = handler.create_daily_note(target_date=test_date)
        content_before = note_path.read_text(encoding='utf-8')

        # Append empty string
        handler.append_to_daily_note("", target_date=test_date)

        # Verify behavior (either skip or create empty item)
        content_after = note_path.read_text(encoding='utf-8')

        # Implementation can choose to:
        # 1. Skip operation (content unchanged)
        # 2. Create empty item "- "
        # Both are acceptable - test checks implementation doesn't crash
        assert note_path.exists()

    def test_append_multiline_text(self, test_vault):
        """Edge case: Handle text with newlines"""
        handler = VaultHandler(str(test_vault))
        test_date = date(2025, 1, 15)

        # Create daily note
        note_path = handler.create_daily_note(target_date=test_date)

        # Append multiline text
        multiline_text = "Line 1\nLine 2\nLine 3"
        handler.append_to_daily_note(multiline_text, target_date=test_date)

        # Verify text appears in file (implementation determines format)
        content = note_path.read_text(encoding='utf-8')

        # Text should appear somewhere in Quick Capture section
        qc_start = content.find("## Quick Capture")
        qc_end = content.find("---", qc_start)
        qc_section = content[qc_start:qc_end]

        # At minimum, the text should be present (may be formatted differently)
        assert "Line 1" in qc_section
        assert "Line 2" in qc_section
        assert "Line 3" in qc_section

    def test_append_very_long_text(self, test_vault):
        """Edge case: Handle very long text (1000+ chars)"""
        handler = VaultHandler(str(test_vault))
        test_date = date(2025, 1, 15)

        # Create daily note
        note_path = handler.create_daily_note(target_date=test_date)

        # Create a very long string (1000 characters)
        long_text = "A" * 1000

        # Append long text
        handler.append_to_daily_note(long_text, target_date=test_date)

        # Verify text fully preserved
        content = note_path.read_text(encoding='utf-8')
        assert long_text in content

        # Verify file I/O handles large content
        assert len(content) > 1000
