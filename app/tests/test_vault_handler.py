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
        handler.append_to_daily_note("Test text")

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
        handler.append_to_daily_note("Test text")

        # Verify note still exists and content unchanged (TODO logic not implemented yet)
        assert note_path.exists()
        current_content = note_path.read_text(encoding='utf-8')
        # Content should be unchanged since append is not yet implemented
        assert current_content == original_content
