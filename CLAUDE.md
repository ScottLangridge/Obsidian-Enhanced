# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Obsidian Enhanced is a FastAPI-based service that enhances Obsidian vault functionality through a web interface. The primary feature is "Quick Capture" - a text processing system that receives text input via API, applies pattern-based classification rules, and routes messages to appropriate handlers (e.g., transforming "pl3" to "Parking Level: 3" in daily notes).

The application runs in Docker and expects an Obsidian vault to be synced to `./vault/` (Syncthing recommended).

## Development Commands

### Running the Application
```bash
# Build and start the service (runs on port 8000)
docker compose up --build

# Run in background
docker compose up -d

# Stop the service
docker compose down
```

### Testing
```bash
# Run all tests
./test.sh

# Run with verbose output
./test.sh -v

# Run specific test file
./test.sh tests/test_message_queue.py

# Run specific test function
./test.sh tests/test_message_queue.py::test_messages_are_queued_and_processed_on_next_arrival
```

### Development Workflow
The Docker container uses `--reload` flag with uvicorn, so code changes in `./app/` are automatically reloaded without restarting the container.

## Architecture

### Core Components

**server.py** - FastAPI application entry point
- Defines API endpoints (`/api/capture` for text capture)
- Serves static web interface at root (`/`)
- Uses BackgroundTasks to process captures asynchronously
- Initializes VaultHandler and QuickCapture on startup

**quick_capture.py** - Pattern-based text classification engine
- Processes incoming text using ordered rule patterns (regex-based)
- First matching rule wins
- Each rule consists of a (pattern, handler) tuple
- Falls back to simple append if no pattern matches
- Example rule: `r'\s*pl(\d)\s*'` → `handle_parking_level()`

**vault_handler.py** - Obsidian vault operations
- Abstraction layer for all vault file operations
- Currently contains placeholder implementation for `append_to_daily_note()`
- Will handle daily note creation, frontmatter, section management

**main.py** - Alternative entry point (imports from server.py)

### Request Flow
1. User submits text via web interface (`static/index.html`)
2. POST request to `/api/capture` with JSON payload `{"text": "..."}`
3. Server adds `quick_capture.process()` to BackgroundTasks queue
4. QuickCapture checks rules in order, calls first matching handler
5. Handler uses VaultHandler to modify vault files

### Adding New Capture Rules

Rules are defined in `quick_capture.py` in the `__init__` method. Add new (pattern, handler) tuples to the `self.rules` list. Rules are checked sequentially - order matters.

Example:
```python
self.rules = [
    (r'\s*pl(\d)\s*', self.handle_parking_level),
    (r'^TODO:\s*(.+)$', self.handle_todo),  # Add new rules here
]
```

Then implement the corresponding handler method:
```python
def handle_todo(self, text: str, match: re.Match) -> None:
    task = match.group(1)
    # Process and use vault_handler to write
```

## Testing

Tests are located in `app/tests/` and use pytest with FastAPI's TestClient. The test suite includes:
- Message queue behavior verification
- Mock-based testing for VaultHandler interactions
- Stdout capture for debugging background task execution

The `test.sh` script runs pytest inside the Docker container to ensure consistent test environment.
