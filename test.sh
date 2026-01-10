#!/bin/bash
# Run tests inside Docker container

docker compose run --rm app pytest tests/ -v "$@"
