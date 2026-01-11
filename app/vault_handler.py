#!/usr/bin/env python3

import logging
import re
from pathlib import Path
from datetime import date, timedelta

logger = logging.getLogger(__name__)

# Templater variable regex patterns
TEMPLATER_YESTERDAY = re.compile(
    r"<%\s*fileDate\s*=\s*moment\(tp\.file\.title,\s*'YYYY-MM-DD'\)\.subtract\(1,\s*'d'\)\.format\('YYYY-MM-DD'\)\s*%>"
)
TEMPLATER_TOMORROW = re.compile(
    r"<%\s*fileDate\s*=\s*moment\(tp\.file\.title,\s*'YYYY-MM-DD'\)\.add\(1,\s*'d'\)\.format\('YYYY-MM-DD'\)\s*%>"
)
TEMPLATER_DATE_NOW = re.compile(r"<%\s*tp\.date\.now\(\)\s*%>")


class VaultHandler:
    """Handles all vault operations"""

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.daily_notes_folder = self.vault_path / "Daily Notes"
        self.template_path = self.vault_path / "一 Obsidian 一" / "Templates" / "Daily Note.md"

    def _process_templater_variables(self, content: str, note_date: date) -> str:
        """Process Templater variables in template content

        Args:
            content: Template content with Templater variables
            note_date: Date of the note being created

        Returns:
            Content with Templater variables replaced with actual dates
        """
        # Replace yesterday
        yesterday = (note_date - timedelta(days=1)).strftime('%Y-%m-%d')
        content = TEMPLATER_YESTERDAY.sub(yesterday, content)

        # Replace tomorrow
        tomorrow = (note_date + timedelta(days=1)).strftime('%Y-%m-%d')
        content = TEMPLATER_TOMORROW.sub(tomorrow, content)

        # Replace current date
        current = note_date.strftime('%Y-%m-%d')
        content = TEMPLATER_DATE_NOW.sub(current, content)

        return content

    def create_daily_note(self, target_date: date = None, exist_ok: bool = False) -> Path:
        """Create a daily note from template for the specified date

        Args:
            target_date: Date for the note (defaults to today)
            exist_ok: If True, return existing note path without error

        Returns:
            Path to the created (or existing) daily note

        Raises:
            FileExistsError: If note exists and exist_ok=False
            FileNotFoundError: If template doesn't exist
        """
        # Default to today
        if target_date is None:
            target_date = date.today()

        # Construct daily note path
        note_filename = target_date.strftime('%Y-%m-%d') + '.md'
        note_path = self.daily_notes_folder / note_filename

        # Check if already exists
        if note_path.exists():
            if exist_ok:
                logger.info(f"Daily note already exists: {note_path}")
                return note_path
            else:
                raise FileExistsError(f"Daily note already exists: {note_path}")

        # Verify template exists
        if not self.template_path.exists():
            raise FileNotFoundError(f"Template not found: {self.template_path}")

        # Read template
        template_content = self.template_path.read_text(encoding='utf-8')

        # Process Templater variables
        processed_content = self._process_templater_variables(template_content, target_date)

        # Ensure daily notes folder exists
        self.daily_notes_folder.mkdir(parents=True, exist_ok=True)

        # Write processed content
        note_path.write_text(processed_content, encoding='utf-8')

        logger.info(f"Created daily note: {note_path}")
        return note_path

    def append_to_daily_note(self, text: str) -> None:
        """Append text to today's daily note (creates note if needed)

        Args:
            text: The text to append
        """
        # Ensure daily note exists
        daily_note_path = self.create_daily_note(exist_ok=True)

        # TODO: Implement section-aware appending (future work)
        logger.info(f"Would append to {daily_note_path}: {text}")
