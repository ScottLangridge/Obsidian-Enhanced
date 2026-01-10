#!/usr/bin/env python3

import logging
import os
from pathlib import Path


# Define log format
LOG_FORMAT = "%(asctime)s - %(levelname)s - [%(name)s] - %(message)s"


def setup_logging():
    """Configure logging for the application

    Sets up dual handlers for console (stdout) and file (./logs/app.log).
    Log level is controlled by LOG_LEVEL environment variable (defaults to INFO).

    Returns:
        dict: Dictionary of configured loggers for each component
    """
    # Get log level from environment variable (default to INFO)
    log_level_name = os.environ.get("LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_name, logging.INFO)

    # Create logs directory if it doesn't exist
    logs_dir = Path("/app/logs")
    logs_dir.mkdir(parents=True, exist_ok=True)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove any existing handlers to avoid duplicates
    root_logger.handlers.clear()

    # Create console handler (stdout)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter(LOG_FORMAT)
    console_handler.setFormatter(console_formatter)

    # Create file handler (./logs/app.log)
    file_handler = logging.FileHandler("/app/logs/app.log", mode="a")
    file_handler.setLevel(log_level)
    file_formatter = logging.Formatter(LOG_FORMAT)
    file_handler.setFormatter(file_formatter)

    # Add handlers to root logger
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    # Create component-specific loggers
    loggers = {
        "SERVER": logging.getLogger("SERVER"),
        "QUICK_CAPTURE": logging.getLogger("QUICK_CAPTURE"),
        "VAULT_HANDLER": logging.getLogger("VAULT_HANDLER"),
    }

    return loggers


def get_logger(name: str) -> logging.Logger:
    """Get a logger by name

    Args:
        name: Name of the logger (e.g., 'SERVER', 'QUICK_CAPTURE', 'VAULT_HANDLER')

    Returns:
        logging.Logger: The requested logger
    """
    return logging.getLogger(name)
