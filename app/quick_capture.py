#!/usr/bin/env python3

import logging
import re
from decimal import Decimal, ROUND_HALF_UP
from vault_handler import VaultHandler

logger = logging.getLogger(__name__)


class QuickCapture:
    """Handles classification and processing of captured text"""

    def __init__(self, vault_handler: VaultHandler):
        self.vault_handler = vault_handler

        # Define classification rules as (pattern, handler) tuples
        # Rules are checked in order - first match wins
        self.rules = [
            (r'^\s*(?:w|weight)\s*(\d+(?:\.\d+)?)\s*$', self.handle_weight),
            (r'^\s*pl(\d)\s*$', self.handle_parking_level),
            (r'^\s*(task|todo)\s([\s\S]+)$', self.handle_todo_task),
            # Add more rules here as needed:
            # (r'^\[\[(.+)\]\]', self.handle_wiki_link),
        ]

    def process(self, text: str) -> None:
        """Process captured text - check rules and route to handler

        Args:
            text: The captured text to process
        """
        logger.info(f"Processing: {text}")

        # Check rules in order - first match wins
        for pattern, handler in self.rules:
            match = re.match(pattern, text, re.IGNORECASE)
            if match:
                handler_name = handler.__name__
                logger.info(f"Matched rule: {pattern}")
                logger.info(f"Calling handler: {handler_name}")
                handler(text, match)
                return

        # No match - use fallback
        logger.info("No rule matched - using fallback")
        self.handle_fallback(text)

    def handle_weight(self, text: str, match: re.Match) -> None:
        """Handle weight captures (e.g., 'w70.3' -> '[weight::70.3]')

        Args:
            text: The original captured text
            match: The regex match object
        """
        weight_value = match.group(1)
        # Use Decimal for proper rounding (round half up) to 1 decimal place
        weight_decimal = Decimal(weight_value)
        rounded_weight = weight_decimal.quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)
        formatted_weight = str(rounded_weight)
        self.vault_handler.populate_weight_tag(formatted_weight)

    def handle_parking_level(self, text: str, match: re.Match) -> None:
        """Handle parking level captures (e.g., 'pl3' -> 'Parking Level: 3')

        Args:
            text: The original captured text
            match: The regex match object
        """
        level = match.group(1)
        formatted_text = f"Parking Level: {level}"
        self.vault_handler.append_to_daily_note(formatted_text)

    def handle_todo_task(self, text: str, match: re.Match) -> None:
        """Handle todo/task captures (e.g., 'task buy milk' -> '- [ ] #todo buy milk')

        Args:
            text: The original captured text
            match: The regex match object
        """
        # Group 1 is 'task' or 'todo' keyword (not needed)
        # Group 2 is the task content (may contain leading/trailing whitespace)
        task_content_raw = match.group(2)

        # Check if content has any non-whitespace characters
        if not task_content_raw.strip():
            self.handle_fallback(text)
            return

        # Strip only trailing whitespace, preserve leading/internal whitespace
        task_content = task_content_raw.rstrip()
        formatted_text = f"- [ ] #todo {task_content}"
        self.vault_handler.append_to_daily_note(formatted_text)

    def handle_fallback(self, text: str) -> None:
        """Fallback handler - add to daily note as-is

        Args:
            text: The captured text to add
        """
        self.vault_handler.append_to_daily_note(text)
