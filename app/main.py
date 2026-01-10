#!/usr/bin/env python3

import logging
from logging_config import setup_logging
from server import app

if __name__ == "__main__":
    # Initialize logging
    setup_logging()
    logger = logging.getLogger("MAIN")

    logger.info("Starting Obsidian Enhanced application")
    logger.info("Server configuration: host=0.0.0.0, port=8000")

    import uvicorn
    try:
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except KeyboardInterrupt:
        logger.info("Shutting down Obsidian Enhanced application")
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        raise
