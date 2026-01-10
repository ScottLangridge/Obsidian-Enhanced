# Logging Feature Implementation Plan

## Overview

Add comprehensive logging to the Obsidian Enhanced application using Python's built-in `logging` module. Replace all existing `print()` statements with proper structured logging that outputs to both console (Docker logs) and persistent log files.

## Requirements Summary

- **Format**: Human-readable text format with timestamps
- **Destination**: Both stdout (Docker console) and `./logs/` directory
- **Log Level**: INFO and above (INFO, WARNING, ERROR, CRITICAL)
- **Scope**: Replace all print statements throughout the application
- **Complexity**: Simple implementation - no advanced features for now

## Implementation Approach

### 1. Create Centralized Logging Configuration

Create a new `app/logging_config.py` module that:
- Configures Python's logging module
- Sets up dual handlers: console (stdout) + file (./logs/app.log)
- Defines consistent log format with timestamps, level, module name, and message
- Allows log level configuration via environment variable `LOG_LEVEL` (defaults to INFO)
- Creates loggers for each component: SERVER, QUICK_CAPTURE, VAULT_HANDLER

### 2. Update Application Components

Replace print statements with proper logging calls in:

**server.py**:
- Line 34: `print(f"[SERVER] Received: {request.text}")` → `logger.info(f"Received: {request.text}")`
- Add request logging for all API endpoints (method, path, status code)
- Add error logging for failed background tasks

**quick_capture.py**:
- Lines 28, 35-36, 41: Replace print statements with appropriate log levels
- INFO: Successful pattern matches and handler routing
- DEBUG: Rule checking details (requires LOG_LEVEL=DEBUG)
- WARNING: Fallback handler usage (unmatched text)

**vault_handler.py**:
- Line 16: Replace placeholder print with actual operation logging
- INFO: Successful vault operations
- ERROR: File operation failures

**main.py**:
- Add startup logging (application start, server configuration)
- Add shutdown logging

### 3. Docker Configuration Updates

**Ensure logs directory exists**:
- Create `./logs/` directory in project root
- Add to `.gitignore` (logs should not be committed)
- Add volume mount in `docker-compose.yml`: `./logs:/app/logs`

**Environment variable support**:
- Add `LOG_LEVEL` environment variable to docker-compose.yml (default: INFO)

### 4. Log Format Specification

```
2026-01-10 15:30:45,123 - INFO - [SERVER] - Received text: hello world
2026-01-10 15:30:45,125 - INFO - [QUICK_CAPTURE] - Processing: hello world
2026-01-10 15:30:45,127 - INFO - [QUICK_CAPTURE] - Matched rule: parking_level
2026-01-10 15:30:45,129 - INFO - [VAULT_HANDLER] - Appended to daily note: 🅿️ Level 3
```

Format: `%(asctime)s - %(levelname)s - [%(name)s] - %(message)s`

## Critical Files to Modify

1. **NEW: app/logging_config.py** - Centralized logging setup
2. **app/server.py** - Replace print statements, add request logging
3. **app/quick_capture.py** - Replace print statements with proper levels
4. **app/vault_handler.py** - Replace print statements
5. **app/main.py** - Add startup/shutdown logging
6. **docker-compose.yml** - Add logs volume mount and LOG_LEVEL env var
7. **.gitignore** - Add logs/ directory

## Implementation Steps

### Step 1: Create Logging Configuration Module

Create `app/logging_config.py`:
- Define log format string
- Create function `setup_logging()` that:
  - Gets LOG_LEVEL from environment (default INFO)
  - Creates logs directory if it doesn't exist
  - Configures root logger
  - Adds console handler (StreamHandler to stdout)
  - Adds file handler (FileHandler to ./logs/app.log)
  - Returns configured loggers for each component

### Step 2: Initialize Logging in Main Entry Point

Update `app/main.py`:
- Import logging_config
- Call `setup_logging()` before starting the server
- Add startup log message
- Consider adding shutdown handler for graceful exit logging

### Step 3: Update Server Module

Update `app/server.py`:
- Import and get logger from logging_config
- Replace print statement at line 34
- Add logging to capture endpoint (start/completion)
- Add error handling with logging for background task failures

### Step 4: Update Quick Capture Module

Update `app/quick_capture.py`:
- Import and get logger from logging_config
- Replace all print statements (lines 28, 35-36, 41)
- Use appropriate log levels:
  - INFO: Processing start, successful matches
  - WARNING: Fallback handler activation
  - DEBUG: Detailed rule checking (for future debugging)

### Step 5: Update Vault Handler Module

Update `app/vault_handler.py`:
- Import and get logger from logging_config
- Replace print statement at line 16
- Add error logging for future file I/O operations
- Add success logging for vault operations

### Step 6: Configure Docker Environment

Update `docker-compose.yml`:
- Add volume mount: `- ./logs:/app/logs` under the app service volumes
- Add environment variable: `LOG_LEVEL: INFO` (or make it configurable)

Create/update `.gitignore`:
- Add `logs/` to prevent committing log files
- Add `*.log` as additional safety

### Step 7: Create Logs Directory

Create `./logs/` directory with appropriate permissions:
- Ensure Docker container can write to it
- Add `.gitkeep` file if you want to track the directory structure

## Configuration Options

### Environment Variables

- `LOG_LEVEL`: Controls verbosity (DEBUG, INFO, WARNING, ERROR, CRITICAL)
  - Development: DEBUG or INFO
  - Production: WARNING or ERROR

### Future Enhancements (Not in Initial Implementation)

- Log rotation (size-based or time-based)
- Structured JSON logging for log aggregation tools
- Correlation IDs for request tracing
- Performance timing metrics
- Separate error log file
- Log compression for old logs

## Verification Plan

### Testing the Logging Implementation

1. **Build and Start Application**:
   ```bash
   docker compose up --build
   ```

2. **Verify Console Logging**:
   - Check startup messages appear in console
   - Observe log format matches specification
   - Verify log level filtering works

3. **Verify File Logging**:
   ```bash
   docker compose run --rm app ls -la /app/logs
   cat ./logs/app.log
   ```
   - Confirm `app.log` file exists
   - Verify same messages appear in both console and file

4. **Test Request Flow**:
   - Open browser to http://localhost:8000
   - Submit test text through the web interface
   - Verify logs show complete request flow:
     - Server receives request
     - Quick capture processes text
     - Pattern matching or fallback
     - Vault handler operation

5. **Test Different Log Levels**:
   ```bash
   # Test DEBUG level
   LOG_LEVEL=DEBUG docker compose up

   # Test WARNING level (should show less output)
   LOG_LEVEL=WARNING docker compose up
   ```

6. **Test Error Logging**:
   - Trigger an error condition (if possible)
   - Verify error messages are logged with appropriate level
   - Check stack traces are captured

7. **Verify Log Persistence**:
   - Stop and restart container
   - Verify log file persists and new logs append to existing file

### Success Criteria

- ✅ No `print()` statements remain in codebase
- ✅ All components use proper loggers
- ✅ Logs appear in both Docker console and `./logs/app.log`
- ✅ Log format is consistent and includes timestamps
- ✅ Log level can be controlled via environment variable
- ✅ Complete request flow is traceable through logs
- ✅ Application starts and runs successfully with logging enabled

## Notes

- Keep implementation simple for initial version
- Focus on replacing existing print statements first
- Ensure logs directory is writable by Docker container
- Consider adding logging to new features as they're developed
- Document logging conventions for future contributors
