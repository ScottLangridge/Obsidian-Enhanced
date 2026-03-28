"""Tests for EMBED journal capture integration"""

import pytest
from unittest.mock import patch
from datetime import date, datetime
from pathlib import Path


class TestAppendToEmbedJournal:
    """Test VaultHandler.append_to_embed_journal with real file operations"""

    @patch('vault_handler.datetime')
    def test_creates_file_when_not_exists(self, mock_datetime, tmp_path):
        """EMBED Journal (Create): Creates journal file when it doesn't exist"""
        from vault_handler import VaultHandler

        mock_datetime.now.return_value = datetime(2026, 5, 3, 9, 15)
        mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

        vh = VaultHandler(str(tmp_path))
        vh.append_to_embed_journal("filter coffee", target_date=date(2026, 5, 3))

        journal_path = tmp_path / "Projects" / "EMBED Study" / "Journal" / "2026-05-03 - EMBED Journal.md"
        assert journal_path.exists()
        content = journal_path.read_text(encoding='utf-8')
        assert content == "- 09:15 - filter coffee\n"

    @patch('vault_handler.datetime')
    def test_creates_directory_structure(self, mock_datetime, tmp_path):
        """EMBED Journal (Directories): Creates nested directory structure"""
        from vault_handler import VaultHandler

        mock_datetime.now.return_value = datetime(2026, 5, 3, 10, 0)
        mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

        vh = VaultHandler(str(tmp_path))
        vh.append_to_embed_journal("test", target_date=date(2026, 5, 3))

        journal_dir = tmp_path / "Projects" / "EMBED Study" / "Journal"
        assert journal_dir.is_dir()

    @patch('vault_handler.datetime')
    def test_appends_to_existing_file(self, mock_datetime, tmp_path):
        """EMBED Journal (Append): Appends entry to existing file"""
        from vault_handler import VaultHandler

        journal_dir = tmp_path / "Projects" / "EMBED Study" / "Journal"
        journal_dir.mkdir(parents=True)
        journal_path = journal_dir / "2026-05-03 - EMBED Journal.md"
        journal_path.write_text("- 09:15 - filter coffee\n", encoding='utf-8')

        mock_datetime.now.return_value = datetime(2026, 5, 3, 10, 30)
        mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

        vh = VaultHandler(str(tmp_path))
        vh.append_to_embed_journal("getting hungry", target_date=date(2026, 5, 3))

        content = journal_path.read_text(encoding='utf-8')
        assert "- 09:15 - filter coffee" in content
        assert "- 10:30 - getting hungry" in content

    @patch('vault_handler.datetime')
    def test_replaces_trailing_placeholder(self, mock_datetime, tmp_path):
        """EMBED Journal (Placeholder): Replaces trailing '- ' placeholder"""
        from vault_handler import VaultHandler

        journal_dir = tmp_path / "Projects" / "EMBED Study" / "Journal"
        journal_dir.mkdir(parents=True)
        journal_path = journal_dir / "2026-05-03 - EMBED Journal.md"
        journal_path.write_text("- 09:15 - filter coffee\n- \n", encoding='utf-8')

        mock_datetime.now.return_value = datetime(2026, 5, 3, 10, 30)
        mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

        vh = VaultHandler(str(tmp_path))
        vh.append_to_embed_journal("getting hungry", target_date=date(2026, 5, 3))

        content = journal_path.read_text(encoding='utf-8')
        assert "- 09:15 - filter coffee" in content
        assert "- 10:30 - getting hungry" in content
        # Placeholder should be replaced, not duplicated
        lines = [l for l in content.split('\n') if l.strip()]
        assert len(lines) == 2

    @patch('vault_handler.datetime')
    def test_auto_adds_timestamp(self, mock_datetime, tmp_path):
        """EMBED Journal (Timestamp): Auto-prepends current time to entry"""
        from vault_handler import VaultHandler

        mock_datetime.now.return_value = datetime(2026, 5, 3, 14, 5)
        mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

        vh = VaultHandler(str(tmp_path))
        vh.append_to_embed_journal("afternoon snack", target_date=date(2026, 5, 3))

        journal_path = tmp_path / "Projects" / "EMBED Study" / "Journal" / "2026-05-03 - EMBED Journal.md"
        content = journal_path.read_text(encoding='utf-8')
        assert "- 14:05 - afternoon snack" in content

    @patch('vault_handler.datetime')
    def test_correct_filename_format(self, mock_datetime, tmp_path):
        """EMBED Journal (Filename): File uses YYYY-MM-DD - EMBED Journal.md format"""
        from vault_handler import VaultHandler

        mock_datetime.now.return_value = datetime(2026, 1, 7, 8, 0)
        mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

        vh = VaultHandler(str(tmp_path))
        vh.append_to_embed_journal("test", target_date=date(2026, 1, 7))

        expected_path = tmp_path / "Projects" / "EMBED Study" / "Journal" / "2026-01-07 - EMBED Journal.md"
        assert expected_path.exists()

    @patch('vault_handler.datetime')
    def test_defaults_to_today(self, mock_datetime, tmp_path):
        """EMBED Journal (Default Date): Defaults to today's date when no date specified"""
        from vault_handler import VaultHandler

        mock_datetime.now.return_value = datetime(2026, 5, 3, 9, 0)
        mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

        with patch('vault_handler.date') as mock_date:
            mock_date.today.return_value = date(2026, 5, 3)
            mock_date.side_effect = lambda *args, **kwargs: date(*args, **kwargs)

            vh = VaultHandler(str(tmp_path))
            vh.append_to_embed_journal("test")

        expected_path = tmp_path / "Projects" / "EMBED Study" / "Journal" / "2026-05-03 - EMBED Journal.md"
        assert expected_path.exists()

    @patch('vault_handler.datetime')
    def test_multiple_entries_same_day(self, mock_datetime, tmp_path):
        """EMBED Journal (Multiple): Multiple entries are added chronologically"""
        from vault_handler import VaultHandler

        journal_dir = tmp_path / "Projects" / "EMBED Study" / "Journal"
        journal_dir.mkdir(parents=True)
        journal_path = journal_dir / "2026-05-03 - EMBED Journal.md"

        vh = VaultHandler(str(tmp_path))

        mock_datetime.now.return_value = datetime(2026, 5, 3, 9, 15)
        mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
        vh.append_to_embed_journal("filter coffee", target_date=date(2026, 5, 3))

        mock_datetime.now.return_value = datetime(2026, 5, 3, 10, 30)
        vh.append_to_embed_journal("getting hungry", target_date=date(2026, 5, 3))

        mock_datetime.now.return_value = datetime(2026, 5, 3, 12, 0)
        vh.append_to_embed_journal("lunch time", target_date=date(2026, 5, 3))

        content = journal_path.read_text(encoding='utf-8')
        lines = [l for l in content.split('\n') if l.strip()]
        assert len(lines) == 3
        assert lines[0] == "- 09:15 - filter coffee"
        assert lines[1] == "- 10:30 - getting hungry"
        assert lines[2] == "- 12:00 - lunch time"


class TestEmbedJournalEndToEnd:
    """End-to-end tests: QuickCapture.process -> VaultHandler -> file system"""

    @patch('vault_handler.datetime')
    def test_e2e_embed_capture(self, mock_datetime, tmp_path):
        """E2E Embed: Full pipeline from 'embed message' to file content"""
        from vault_handler import VaultHandler
        from quick_capture import QuickCapture

        mock_datetime.now.return_value = datetime(2026, 5, 3, 9, 15)
        mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

        with patch('vault_handler.date') as mock_date:
            mock_date.today.return_value = date(2026, 5, 3)
            mock_date.side_effect = lambda *args, **kwargs: date(*args, **kwargs)

            vh = VaultHandler(str(tmp_path))
            qc = QuickCapture(vh)
            qc.process("embed filter coffee")

        journal_path = tmp_path / "Projects" / "EMBED Study" / "Journal" / "2026-05-03 - EMBED Journal.md"
        assert journal_path.exists()
        content = journal_path.read_text(encoding='utf-8')
        assert "- 09:15 - filter coffee" in content

    @patch('vault_handler.datetime')
    def test_e2e_embed_case_insensitive(self, mock_datetime, tmp_path):
        """E2E Embed (Case): 'EMBED test' works end to end"""
        from vault_handler import VaultHandler
        from quick_capture import QuickCapture

        mock_datetime.now.return_value = datetime(2026, 5, 3, 10, 0)
        mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

        with patch('vault_handler.date') as mock_date:
            mock_date.today.return_value = date(2026, 5, 3)
            mock_date.side_effect = lambda *args, **kwargs: date(*args, **kwargs)

            vh = VaultHandler(str(tmp_path))
            qc = QuickCapture(vh)
            qc.process("EMBED test message")

        journal_path = tmp_path / "Projects" / "EMBED Study" / "Journal" / "2026-05-03 - EMBED Journal.md"
        content = journal_path.read_text(encoding='utf-8')
        assert "- 10:00 - test message" in content

    @patch('vault_handler.datetime')
    def test_e2e_embed_multiple_captures(self, mock_datetime, tmp_path):
        """E2E Embed (Multiple): Multiple captures build up journal"""
        from vault_handler import VaultHandler
        from quick_capture import QuickCapture

        mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

        with patch('vault_handler.date') as mock_date:
            mock_date.today.return_value = date(2026, 5, 3)
            mock_date.side_effect = lambda *args, **kwargs: date(*args, **kwargs)

            vh = VaultHandler(str(tmp_path))
            qc = QuickCapture(vh)

            mock_datetime.now.return_value = datetime(2026, 5, 3, 9, 15)
            qc.process("embed filter coffee")

            mock_datetime.now.return_value = datetime(2026, 5, 3, 10, 30)
            qc.process("embed getting hungry")

        journal_path = tmp_path / "Projects" / "EMBED Study" / "Journal" / "2026-05-03 - EMBED Journal.md"
        content = journal_path.read_text(encoding='utf-8')
        assert "- 09:15 - filter coffee" in content
        assert "- 10:30 - getting hungry" in content

    @patch('vault_handler.datetime')
    def test_e2e_embed_comma_separator(self, mock_datetime, tmp_path):
        """E2E Embed (Comma): 'embed, message' works with comma separator (speech recognition)"""
        from vault_handler import VaultHandler
        from quick_capture import QuickCapture

        mock_datetime.now.return_value = datetime(2026, 5, 3, 9, 15)
        mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

        with patch('vault_handler.date') as mock_date:
            mock_date.today.return_value = date(2026, 5, 3)
            mock_date.side_effect = lambda *args, **kwargs: date(*args, **kwargs)

            vh = VaultHandler(str(tmp_path))
            qc = QuickCapture(vh)
            qc.process("embed, filter coffee")

        journal_path = tmp_path / "Projects" / "EMBED Study" / "Journal" / "2026-05-03 - EMBED Journal.md"
        content = journal_path.read_text(encoding='utf-8')
        assert "- 09:15 - filter coffee" in content

    @patch('vault_handler.datetime')
    def test_e2e_food_log_comma_separator(self, mock_datetime, tmp_path):
        """E2E Food Log (Comma): 'food log, entry' works with comma separator (speech recognition)"""
        from vault_handler import VaultHandler
        from quick_capture import QuickCapture

        mock_datetime.now.return_value = datetime(2026, 5, 3, 12, 0)
        mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

        with patch('vault_handler.date') as mock_date:
            mock_date.today.return_value = date(2026, 5, 3)
            mock_date.side_effect = lambda *args, **kwargs: date(*args, **kwargs)

            vh = VaultHandler(str(tmp_path))
            qc = QuickCapture(vh)
            qc.process("food log, banana")

        journal_path = tmp_path / "Projects" / "EMBED Study" / "Journal" / "2026-05-03 - EMBED Journal.md"
        content = journal_path.read_text(encoding='utf-8')
        assert "- 12:00 - banana" in content

    @patch('vault_handler.datetime')
    def test_e2e_food_diary_comma_separator(self, mock_datetime, tmp_path):
        """E2E Food Diary (Comma): 'food diary, entry' works with comma separator"""
        from vault_handler import VaultHandler
        from quick_capture import QuickCapture

        mock_datetime.now.return_value = datetime(2026, 5, 3, 8, 30)
        mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

        with patch('vault_handler.date') as mock_date:
            mock_date.today.return_value = date(2026, 5, 3)
            mock_date.side_effect = lambda *args, **kwargs: date(*args, **kwargs)

            vh = VaultHandler(str(tmp_path))
            qc = QuickCapture(vh)
            qc.process("food diary, oats")

        journal_path = tmp_path / "Projects" / "EMBED Study" / "Journal" / "2026-05-03 - EMBED Journal.md"
        content = journal_path.read_text(encoding='utf-8')
        assert "- 08:30 - oats" in content
