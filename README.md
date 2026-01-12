# Obsidian Enhanced

A Python application for enhancing Obsidian vault functionality through a FastAPI-based web service.

## Features

- **Quick Capture**: Text processing system with pattern-based classification
- **Parking Level Tracking**: Automatically formats parking level entries
- **Weight Tracking**: Capture and track weight measurements
- **Todo/Task Management**: Intelligent task capture with date handling

## Setup

### Prerequisites

- Docker and Docker Compose
- An Obsidian vault synced to a location on your machine (Syncthing recommended)

### Configuration

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd obsidian-enhanced
   ```

2. **Configure your vault location**

   Create a `.env` file in the project root:
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and set your vault path:
   ```bash
   # Use absolute path (recommended for clarity)
   OBSIDIAN_VAULT_PATH=/home/username/Documents/ObsidianVault

   # Or relative path from project root
   OBSIDIAN_VAULT_PATH=./my-vault

   # Or home directory expansion (Docker Compose will expand ~)
   OBSIDIAN_VAULT_PATH=~/Obsidian/MyVault
   ```

3. **Ensure your vault has the required structure**

   Your vault should contain:
   - `Daily Notes/` folder (created automatically if missing)
   - `一 Obsidian 一/Templates/Daily Note.md` template file

   The template should include:
   - `## Quick Capture` section
   - `## Trackers` section with `- [weight::]` tag

### Running the Application

```bash
# Start the service
make run
# or
docker compose up -d

# View logs
docker compose logs -f

# Stop the service
make down
# or
docker compose down
```

The web interface will be available at `http://localhost:8000`

## Development

See [CLAUDE.md](CLAUDE.md) for detailed development guidance.

### Quick Commands

```bash
make help       # View all available commands
make test       # Run tests
make test-cov   # Run tests with coverage
make shell      # Open shell in new container
make attach     # Attach to running container
```

## Vault Syncing

We recommend using [Syncthing](https://syncthing.net/) to sync your Obsidian vault to the configured location. This allows the application to access your vault while keeping it synchronized across devices.

**Alternative sync methods:**
- Direct mount if vault is on the same machine
- Network share (NFS, SMB)
- Any other file sync solution (Dropbox, Google Drive, etc.)

## Architecture

- **FastAPI** web framework for API and static file serving
- **Docker** containerization for consistent deployment
- **Pytest** for testing with high coverage requirements
- Pattern-based text classification engine for intelligent message routing

## Troubleshooting

**"Template not found" error:**
- Ensure your vault path is correctly configured in `.env`
- Verify the template exists at `一 Obsidian 一/Templates/Daily Note.md` in your vault
- Check Docker logs: `docker compose logs app`

**Permission errors:**
- Ensure the vault directory is readable/writable by the Docker user
- Check file permissions on your host system

**Changes not reflecting:**
- The container uses auto-reload, but you may need to restart: `make restart`
