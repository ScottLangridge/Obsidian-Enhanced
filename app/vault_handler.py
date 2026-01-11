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

# Quick Capture constants
QUICK_CAPTURE_HEADING = "## Quick Capture"
PLACEHOLDER_PATTERN = re.compile(r'^-\s*$')  # Matches "-", "- ", "-  ", "-\t", etc.
SECTION_SEPARATOR = "---"

# Trackers constants
TRACKERS_HEADING = "## Trackers"
WEIGHT_TAG_PATTERN = re.compile(r'^\s*-\s*\[weight::(?:\d+(?:\.\d+)?)?\]\s*$')  # Matches "- [weight::]" or "- [weight::70.3]"


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

    def _find_section(self, lines: list[str], heading: str) -> tuple[int, int] | None:
        """Find a section by heading

        Args:
            lines: List of lines from the note file
            heading: The heading to search for (e.g., "## Quick Capture")

        Returns:
            Tuple of (start_idx, end_idx) for the section,
            or None if section not found.
            start_idx points to the heading line
            end_idx points to the line after the last line of the section
        """
        # Find the heading
        heading_idx = None
        for i, line in enumerate(lines):
            if line.strip() == heading:
                heading_idx = i
                break
        else:
            return None  # Section not found

        # Find the end of the section (next --- or next ## heading)
        end_idx = None
        for i in range(heading_idx + 1, len(lines)):
            line = lines[i].strip()
            if line == SECTION_SEPARATOR or line.startswith("##"):
                end_idx = i
                break
        else:
            # No separator or next heading found, section goes to end of file
            end_idx = len(lines)

        return (heading_idx, end_idx)

    def _find_quick_capture_section(self, lines: list[str]) -> tuple[int, int] | None:
        """Find the Quick Capture section boundaries

        Args:
            lines: List of lines from the note file

        Returns:
            Tuple of (start_idx, end_idx) for the Quick Capture section,
            or None if section not found.
            start_idx points to the "## Quick Capture" line
            end_idx points to the line after the last line of the section
        """
        return self._find_section(lines, QUICK_CAPTURE_HEADING)

    def _has_placeholder(self, section_lines: list[str]) -> tuple[bool, int | None]:
        """Check if section has placeholder line

        Args:
            section_lines: Lines in the Quick Capture section (between heading and separator)

        Returns:
            Tuple of (has_placeholder, placeholder_index)
        """
        for idx, line in enumerate(section_lines):
            if PLACEHOLDER_PATTERN.match(line):
                return (True, idx)
        return (False, None)

    def append_to_daily_note(self, text: str, target_date: date = None) -> None:
        """Append text to daily note Quick Capture section

        First capture of the day replaces the '- ' placeholder.
        Subsequent captures are inserted at the top of the list (newest first).

        Args:
            text: The text to append (will be formatted as '- {text}')
            target_date: Date of the note (defaults to today)
        """
        try:
            # Ensure daily note exists
            daily_note_path = self.create_daily_note(target_date=target_date, exist_ok=True)

            # Read file content
            try:
                content = daily_note_path.read_text(encoding='utf-8')
            except UnicodeDecodeError as e:
                logger.error(f"Encoding error reading {daily_note_path}: {e}")
                return
            except PermissionError as e:
                logger.error(f"Permission denied reading {daily_note_path}: {e}")
                return

            lines = content.split('\n')

            # Find Quick Capture section
            section_bounds = self._find_quick_capture_section(lines)
            if section_bounds is None:
                logger.error("Quick Capture section not found in daily note")
                return

            start_idx, end_idx = section_bounds

            # Analyze section content
            section_lines = lines[start_idx + 1:end_idx]  # Lines between heading and separator
            has_placeholder, placeholder_idx = self._has_placeholder(section_lines)

            # Create new item line
            new_item = f"- {text}"

            # Modify section based on mode
            if has_placeholder:
                # REPLACE mode: Replace placeholder with new text
                section_lines[placeholder_idx] = new_item
            else:
                # INSERT mode: Insert at beginning of section
                section_lines.insert(0, new_item)

            # Reconstruct file
            new_lines = (
                lines[:start_idx+1] +  # Everything up to and including heading
                section_lines +         # Modified Quick Capture content
                lines[end_idx:]         # Everything after Quick Capture section
            )
            new_content = '\n'.join(new_lines)

            # Write back to file
            try:
                daily_note_path.write_text(new_content, encoding='utf-8')
                logger.info(f"Appended to Quick Capture: {text}")
            except PermissionError as e:
                logger.error(f"Permission denied writing {daily_note_path}: {e}")
                return

        except Exception as e:
            logger.exception(f"Unexpected error appending to daily note: {e}")
            raise

    def populate_weight_tag(self, weight_value: str, target_date: date = None) -> None:
        """Populate the [weight::] tag in the Trackers section

        Args:
            weight_value: The weight value formatted to 1 decimal place (e.g., "70.3")
            target_date: Date of the note (defaults to today)
        """
        try:
            # Ensure daily note exists
            daily_note_path = self.create_daily_note(target_date=target_date, exist_ok=True)

            # Read file content
            try:
                content = daily_note_path.read_text(encoding='utf-8')
            except UnicodeDecodeError as e:
                logger.error(f"Encoding error reading {daily_note_path}: {e}")
                return
            except PermissionError as e:
                logger.error(f"Permission denied reading {daily_note_path}: {e}")
                return

            lines = content.split('\n')

            # Find Trackers section
            section_bounds = self._find_section(lines, TRACKERS_HEADING)
            if section_bounds is None:
                logger.error("Trackers section not found in daily note")
                return

            start_idx, end_idx = section_bounds

            # Find and replace the weight tag line
            section_lines = lines[start_idx + 1:end_idx]
            weight_tag_found = False

            for idx, line in enumerate(section_lines):
                if WEIGHT_TAG_PATTERN.match(line):
                    # Replace the empty tag with populated value
                    section_lines[idx] = f"- [weight::{weight_value}]"
                    weight_tag_found = True
                    break

            if not weight_tag_found:
                logger.error("Weight tag [weight::] not found in Trackers section")
                return

            # Reconstruct file
            new_lines = (
                lines[:start_idx+1] +  # Everything up to and including heading
                section_lines +         # Modified Trackers content
                lines[end_idx:]         # Everything after Trackers section
            )
            new_content = '\n'.join(new_lines)

            # Write back to file
            try:
                daily_note_path.write_text(new_content, encoding='utf-8')
                logger.info(f"Populated weight tag with: {weight_value}")
            except PermissionError as e:
                logger.error(f"Permission denied writing {daily_note_path}: {e}")
                return

        except Exception as e:
            logger.exception(f"Unexpected error populating weight tag: {e}")
            raise
