.PHONY: help test test-cov shell attach run build up down restart clean

help:
	@echo "Available commands:"
	@echo "  make test          - Run tests"
	@echo "  make test-cov      - Run tests with coverage report"
	@echo "  make shell         - Open shell in new container"
	@echo "  make attach        - Attach to shell of running container"
	@echo "  make run           - Start services in detached mode"
	@echo "  make build         - Build Docker image"
	@echo "  make up            - Start services in detached mode"
	@echo "  make down          - Stop services"
	@echo "  make restart       - Restart services"
	@echo "  make clean         - Remove stopped containers and clean up"

test:
	docker compose run --rm app pytest tests/ -v

test-cov:
	docker compose run --rm app pytest tests/ --cov=app --cov-report=html --cov-report=term

shell:
	docker compose run --rm app bash

attach:
	docker compose exec app bash

run:
	docker compose up -d

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

restart:
	docker compose restart

clean:
	docker compose down -v
	docker system prune -f
