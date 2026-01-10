#!/usr/bin/env python3

import re
from vault_handler import VaultHandler


class QuickCapture:
    """Handles classification and processing of captured text"""

    def __init__(self, vault_handler: VaultHandler):
        self.vault_handler = vault_handler

        # Define classification rules as (pattern, handler) tuples
        # Rules are checked in order - first match wins
        self.rules = [
            (r'\s*pl(\d)\s*', self.handle_parking_level),
            # Add more rules here as needed:
            # (r'^TODO:\s*(.+)$', self.handle_todo),
            # (r'^\[\[(.+)\]\]', self.handle_wiki_link),
        ]

    def process(self, text: str) -> None:
        """Process captured text - check rules and route to handler

        Args:
            text: The captured text to process
        """
        print(f"[QUICK_CAPTURE] Processing: {text}")

        # Check rules in order - first match wins
        for pattern, handler in self.rules:
            match = re.match(pattern, text, re.IGNORECASE)
            if match:
                handler_name = handler.__name__
                print(f"[QUICK_CAPTURE] Matched rule: {pattern}")
                print(f"[QUICK_CAPTURE] Calling handler: {handler_name}")
                handler(text, match)
                return

        # No match - use fallback
        print(f"[QUICK_CAPTURE] No rule matched - using fallback")
        self.handle_fallback(text)

    def handle_parking_level(self, text: str, match: re.Match) -> None:
        """Handle parking level captures (e.g., 'pl3' -> 'Parking Level: 3')

        Args:
            text: The original captured text
            match: The regex match object
        """
        level = match.group(1)
        formatted_text = f"Parking Level: {level}"
        self.vault_handler.append_to_daily_note(formatted_text)

    def handle_fallback(self, text: str) -> None:
        """Fallback handler - add to daily note as-is

        Args:
            text: The captured text to add
        """
        self.vault_handler.append_to_daily_note(text)
