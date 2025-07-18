# Makefile for Koinonia House Project

# Default command
.DEFAULT_GOAL := help

# Use bash for commands
SHELL := /bin/bash

# Docker Compose command
COMPOSE := docker-compose

## --------------------------------------
## General Development Commands
## --------------------------------------

.PHONY: up
up: ## 🚀 Start all services in detached mode
	@echo "Starting all services..."
	$(COMPOSE) up --build -d

.PHONY: down
down: ## ⏹️ Stop and remove all services
	@echo "Stopping all services..."
	$(COMPOSE) down

.PHONY: backend-only
backend-only: ## ⚙️ Start only the backend and its database dependencies
	@echo "Starting backend and its dependencies..."
	$(COMPOSE) up --build -d fastapi-backend timescaledb milvus neo4j etcd minio

.PHONY: frontend-only
frontend-only: ## 🎨 Run the frontend development server directly
	@echo "Starting frontend development server on http://localhost:3000..."
	@echo "NOTE: The backend must be running separately for API calls to work."
	cd frontend && npm install && npm run dev

## --------------------------------------
## Logging and Status
## --------------------------------------

.PHONY: logs
logs: ## 📜 View logs for all running services
	@echo "Tailing logs for all services..."
	$(COMPOSE) logs -f

.PHONY: logs-backend
logs-backend: ## 📜 View logs for the backend service only
	@echo "Tailing logs for the backend service..."
	$(COMPOSE) logs -f fastapi-backend

.PHONY: ps
ps: ## 📊 List all running containers
	@echo "Current running containers:"
	$(COMPOSE) ps

## --------------------------------------
## Data and Testing
## --------------------------------------

.PHONY: ingest
ingest: ## 📥 Run the data ingestion pipeline
	@echo "Running the data ingestion script inside the backend container..."
	@echo "This may take a significant amount of time. Please be patient."
	$(COMPOSE) exec fastapi-backend python -m data_ingestion.ingest

.PHONY: test-backend
test-backend: ## 🧪 Run the backend test suite
	@echo "Running backend tests..."
	$(COMPOSE) exec fastapi-backend poetry run pytest

## --------------------------------------
## System Maintenance
## --------------------------------------

.PHONY: prune
prune: down ## 🧹 Stop services and remove all unused Docker data (containers, networks, volumes)
	@echo "Removing unused Docker containers, networks, and volumes..."
	docker system prune -af --volumes

.PHONY: help
help: ## 🆘 Display this help screen
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: poetry-lock
poetry-lock: ## 🔄 Regenerate poetry.lock file
	@echo "Updating poetry.lock file..."
	$(COMPOSE) run --rm fastapi-backend poetry lock
