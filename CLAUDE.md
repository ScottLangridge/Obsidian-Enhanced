# Claude Workspace

## Obsidian Vault Integration

`/mnt/c/Users/scott/Documents/Obsidian Vaults/Scott's Vault/Projects/Obsidian Enhanced/Claude Workspace` is a section of the Obsidian vault dedicated to Claude for this project.

This directory will be used for:
- Scratch work and temporary notes
- Planning and design documents
- Memory and context persistence across sessions

## Obsidian File Formatting Guidelines

When creating markdown files in the Obsidian workspace:
- **Do NOT use a level 1 heading (#) for the title**
- Obsidian implicitly treats the filename as the title
- Start the document content with level 2 headings (##) or lower
- Example: A file named "Project Overview.md" should start with `## Section Name`, not `# Project Overview`

## Docker Setup

This project uses Docker Compose for development:

### Structure
```
/home/scott/docker/obsidian-enhanced/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── app/              # Python application code
    └── main.py
```

### Configuration Philosophy
- **Dockerfile**: Handles environment setup (Python image, dependencies, working directory, default command)
- **docker-compose.yml**: Handles development workflow (build, volume mount, port mapping)
- **No redundancy**: Settings are defined once - either in Dockerfile or docker-compose, not both
- **Volume mount**: `./app:/app` mounts the local app directory to `/app` in the container for live code updates

### Key Decisions
- Application code lives in `./app/` subdirectory (separate from Docker config files)
- Dockerfile only copies `requirements.txt` for dependency installation
- Application code is NOT copied into the image - it's mounted via volume for development
- Container inherits WORKDIR and CMD from Dockerfile (not redefined in docker-compose)
- When the main Python process exits, the container stops (expected behavior for script execution)
