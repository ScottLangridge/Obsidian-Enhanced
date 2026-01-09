# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Obsidian Enhanced is a Python application for enhancing Obsidian vault functionality. The project uses Docker for development and has direct access to an Obsidian vault mounted at `./vault/`.

## Common Commands

### Docker Operations
```bash
# Build and run the application
docker compose up --build

# Run the application (after initial build)
docker compose up

# Rebuild the Docker image
docker compose build

# Stop the application
docker compose down

# Run a Python script in the container
docker compose run --rm app python <script_name>.py

# Access container shell
docker compose run --rm app bash
```

### Development
- Python code goes in `./app/` directory
- Changes to Python files are reflected immediately via volume mount (no rebuild needed)
- Changes to `requirements.txt` require rebuilding the Docker image

## Architecture

### Project Structure
```
/home/scott/docker/obsidian-enhanced/
├── Dockerfile              # Python 3.11 image with dependencies
├── docker-compose.yml      # Development orchestration
├── requirements.txt        # Python dependencies (currently empty)
├── app/                    # Python application code (volume mounted)
│   └── main.py            # Entry point
└── vault/                  # Obsidian vault (volume mounted, read-only access)
    ├── Daily Notes/       # Daily note entries
    ├── Projects/          # Project notes
    ├── Repositories/      # Repository documentation
    ├── Themes/            # Theme notes
    └── ...
```

### Docker Configuration Philosophy
- **Dockerfile**: Handles environment setup (Python image, dependencies, working directory, default command)
- **docker-compose.yml**: Handles development workflow (build, volume mount, port mapping)
- **No redundancy**: Settings are defined once - either in Dockerfile or docker-compose, not both
- **Volume mounts**:
  - `./app:/app` - Application code (live updates during development)
  - `./vault:/vault` - Obsidian vault (synced from external source)

### Key Implementation Details
- Application code lives in `./app/` subdirectory (separate from Docker config files)
- Dockerfile only copies `requirements.txt` for dependency installation
- Application code is NOT copied into the image - it's mounted via volume for development
- Container inherits WORKDIR (`/app`) and CMD from Dockerfile
- When the main Python process exits, the container stops (expected behavior for script execution)
- Port 8000 is mapped for future web server functionality

## Vault Integration

### Vault Syncing
The `./vault/` directory contains a synced Obsidian vault (synced externally via Syncthing or similar). This vault contains:
- Daily Notes - Timestamped daily entries
- Projects - Project-specific notes and documentation
- Repositories - Repository-related notes
- Themes - Thematic organization
- Other user-created folders

### Claude Workspace
`/mnt/c/Users/scott/Documents/Obsidian Vaults/Scott's Vault/Projects/Obsidian Enhanced/Claude Workspace` is a dedicated section of the Obsidian vault for Claude to use for:
- Scratch work and temporary notes
- Planning and design documents
- Memory and context persistence across sessions

### Obsidian File Formatting Guidelines
When creating markdown files in the Obsidian workspace:
- **Do NOT use a level 1 heading (#) for the title**
- Obsidian implicitly treats the filename as the title
- Start the document content with level 2 headings (##) or lower
- Example: A file named "Project Overview.md" should start with `## Section Name`, not `# Project Overview`

## Development Notes

- Currently in early development stage with minimal functionality
- No test suite present yet
- No linting or formatting tools configured yet
- Python dependencies should be added to `requirements.txt` and require image rebuild
