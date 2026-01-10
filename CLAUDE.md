# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Obsidian Enhanced is a FastAPI-based service that enhances Obsidian vault functionality through a web interface. The primary feature is "Quick Capture" - a text processing system that receives text input via API, applies pattern-based classification rules, and routes messages to appropriate handlers (e.g., transforming "pl3" to "Parking Level: 3" in daily notes).

The application runs in Docker and expects an Obsidian vault to be synced to `./vault/` (Syncthing recommended).

## Development Commands

### Makefile Commands
A Makefile is provided for convenient access to common development tasks:

```bash
# View all available commands
make help

# Run tests
make test          # Run tests with verbose output
make test-cov      # Run tests with coverage report (HTML + terminal)

# Container management
make run           # Start services in detached mode (same as make up)
make up            # Start services in detached mode
make down          # Stop services
make build         # Build Docker image
make restart       # Restart services

# Shell access
make shell         # Open bash shell in new container
make attach        # Attach to bash shell of running container

# Cleanup
make clean         # Remove containers and prune Docker system
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

## Testing

Tests are located in `app/tests/` and use pytest with FastAPI's TestClient. The test suite includes:
- Message queue behavior verification
- Mock-based testing for VaultHandler interactions
- Stdout capture for debugging background task execution
- Tests should be written in advance of new features, following test driven development principles.
