# Better Transfer Project Makefile
# This file contains common commands for development and deployment

# Variables
DOCKER_COMPOSE = docker-compose
APP_NAME = better-transfer
CONTAINER_NAME = better-transfer-app-1

# Default target
.DEFAULT_GOAL := help

# Colors for output
BLUE = \033[0;34m
GREEN = \033[0;32m
YELLOW = \033[1;33m
RED = \033[0;31m
NC = \033[0m # No Color

##@ Help
help: ## Display this help message
    @echo "$(BLUE)Better Transfer Project Commands$(NC)"
    @echo ""
    @awk 'BEGIN {FS = ":.*##"; printf "Usage:\n  make $(GREEN)<target>$(NC)\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2 } /^##@/ { printf "\n$(YELLOW)%s$(NC)\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Setup
setup: ## Initial project setup (copy env file)
    @echo "$(BLUE)Setting up Better Transfer project...$(NC)"
    @if [ ! -f .env ]; then \
        echo "$(YELLOW)Creating .env file from template...$(NC)"; \
        cp .env.example .env; \
        echo "$(GREEN)✓ .env file created. Please edit it with your credentials.$(NC)"; \
    else \
        echo "$(YELLOW)⚠ .env file already exists$(NC)"; \
    fi

install: setup build ## Complete installation (setup + build)
    @echo "$(GREEN)✓ Installation complete!$(NC)"

##@ Development
build: ## Build the Docker image
    @echo "$(BLUE)Building Docker image...$(NC)"
    $(DOCKER_COMPOSE) build
    @echo "$(GREEN)✓ Build complete$(NC)"

up: ## Start all services
    @echo "$(BLUE)Starting Better Transfer services...$(NC)"
    $(DOCKER_COMPOSE) up -d
    @echo "$(GREEN)✓ Services started$(NC)"
    @echo "$(YELLOW)App available at: http://localhost:8000$(NC)"

down: ## Stop all services
    @echo "$(BLUE)Stopping services...$(NC)"
    $(DOCKER_COMPOSE) down
    @echo "$(GREEN)✓ Services stopped$(NC)"

restart: down up ## Restart all services

dev: ## Start services and follow logs
    @echo "$(BLUE)Starting services in development mode...$(NC)"
    $(DOCKER_COMPOSE) up

##@ Logs and Monitoring
logs: ## Show logs for all services
    $(DOCKER_COMPOSE) logs

logs-app: ## Show logs for the app service only
    $(DOCKER_COMPOSE) logs -f app

logs-tail: ## Follow logs for all services
    $(DOCKER_COMPOSE) logs -f

status: ## Show status of all services
    $(DOCKER_COMPOSE) ps

##@ Database and Cache
seed: ## Run database seeding scripts
    @echo "$(BLUE)Seeding database...$(NC)"
    $(DOCKER_COMPOSE) exec app python scripts/seed_scripts/seed_all.py
    @echo "$(GREEN)✓ Database seeded$(NC)"

cache-clear: ## Clear Redis cache
    @echo "$(BLUE)Clearing Redis cache...$(NC)"
    $(DOCKER_COMPOSE) exec app python -c "from app.core.redis_client import RedisClient; RedisClient().client.flushall()"
    @echo "$(GREEN)✓ Cache cleared$(NC)"

##@ Testing
test: ## Run all tests
    @echo "$(BLUE)Running tests...$(NC)"
    $(DOCKER_COMPOSE) exec app python -m pytest tests/ -v
    @echo "$(GREEN)✓ Tests complete$(NC)"

test-unit: ## Run unit tests only
    $(DOCKER_COMPOSE) exec app python -m pytest tests/unit/ -v

test-api: ## Run API tests only
    $(DOCKER_COMPOSE) exec app python -m pytest tests/api/ -v

test-coverage: ## Run tests with coverage report
    $(DOCKER_COMPOSE) exec app python -m pytest tests/ --cov=app --cov-report=html
    @echo "$(GREEN)Coverage report generated in htmlcov/$(NC)"

##@ Code Quality
lint: ## Run code linting
    @echo "$(BLUE)Running linter...$(NC)"
    $(DOCKER_COMPOSE) exec app python -m flake8 app/ RAG/
    @echo "$(GREEN)✓ Linting complete$(NC)"

format: ## Format code with black
    @echo "$(BLUE)Formatting code...$(NC)"
    $(DOCKER_COMPOSE) exec app python -m black app/ RAG/
    @echo "$(GREEN)✓ Code formatted$(NC)"

check: lint test ## Run linting and tests

##@ Shell and Debugging
shell: ## Open shell in the app container
    $(DOCKER_COMPOSE) exec app /bin/bash

shell-python: ## Open Python shell in the app container
    $(DOCKER_COMPOSE) exec app python

debug: ## Start services with debug mode
    $(DOCKER_COMPOSE) up app

##@ Cleanup
clean: ## Remove containers and images
    @echo "$(BLUE)Cleaning up containers and images...$(NC)"
    $(DOCKER_COMPOSE) down --rmi all --volumes --remove-orphans
    @echo "$(GREEN)✓ Cleanup complete$(NC)"

clean-cache: ## Remove Docker build cache
    docker system prune -f
    @echo "$(GREEN)✓ Docker cache cleaned$(NC)"

reset: clean build up ## Complete reset (clean + build + up)

##@ Production
prod-build: ## Build production image
    @echo "$(BLUE)Building production image...$(NC)"
    docker build -f Dockerfile.prod -t $(APP_NAME):latest .
    @echo "$(GREEN)✓ Production image built$(NC)"

prod-up: ## Start production services
    $(DOCKER_COMPOSE) -f docker-compose.prod.yml up -d

prod-down: ## Stop production services
    $(DOCKER_COMPOSE) -f docker-compose.prod.yml down

prod-logs: ## Show production logs
    $(DOCKER_COMPOSE) -f docker-compose.prod.yml logs -f

##@ Health Checks
health: ## Check application health
    @echo "$(BLUE)Checking application health...$(NC)"
    @curl -f http://localhost:8000/health > /dev/null 2>&1 && \
        echo "$(GREEN)✓ Application is healthy$(NC)" || \
        echo "$(RED)✗ Application is not responding$(NC)"

ping: ## Ping the application
    curl -f http://localhost:8000/health

##@ Utilities
env-check: ## Check if required environment variables are set
    @echo "$(BLUE)Checking environment variables...$(NC)"
    @if [ -f .env ]; then \
        echo "$(GREEN)✓ .env file exists$(NC)"; \
        if grep -q "OPENAI_API_KEY=" .env && ! grep -q "OPENAI_API_KEY=$$" .env; then \
            echo "$(GREEN)✓ OPENAI_API_KEY is set$(NC)"; \
        else \
            echo "$(RED)✗ OPENAI_API_KEY is not set$(NC)"; \
        fi; \
        if grep -q "MONGO_DB_PCC_CLUSTER_CONNECTION_URL=" .env && ! grep -q "MONGO_DB_PCC_CLUSTER_CONNECTION_URL=$$" .env; then \
            echo "$(GREEN)✓ MongoDB connection is configured$(NC)"; \
        else \
            echo "$(RED)✗ MongoDB connection is not configured$(NC)"; \
        fi; \
    else \
        echo "$(RED)✗ .env file not found. Run 'make setup' first$(NC)"; \
    fi

backup: ## Create backup of important files
    @echo "$(BLUE)Creating backup...$(NC)"
    @mkdir -p backups
    @tar -czf backups/better-transfer-backup-$(shell date +%Y%m%d_%H%M%S).tar.gz \
        --exclude=backups \
        --exclude=.git \
        --exclude=__pycache__ \
        --exclude=.pytest_cache \
        --exclude=htmlcov \
        --exclude=.env \
        .
    @echo "$(GREEN)✓ Backup created in backups/$(NC)"

##@ Documentation
docs: ## Generate API documentation
    @echo "$(BLUE)Generating API documentation...$(NC)"
    $(DOCKER_COMPOSE) exec app python -c "import uvicorn; uvicorn.run('app.main:app', host='0.0.0.0', port=8000)"
    @echo "$(YELLOW)API docs available at: http://localhost:8000/docs$(NC)"

##@ Quick Start
quick-start: setup build up health ## Complete quick start setup
    @echo ""
    @echo "$(GREEN)🎉 Better Transfer is ready!$(NC)"
    @echo ""
    @echo "$(YELLOW)Next steps:$(NC)"
    @echo "  1. Edit .env file with your credentials"
    @echo "  2. Visit http://localhost:8000/docs for API documentation"
    @echo "  3. Run 'make seed' to populate the database"
    @echo "  4. Run 'make logs-app' to monitor application logs"
    @echo ""

.PHONY: help setup install build up down restart dev logs logs-app logs-tail status \
        seed cache-clear test test-unit test-api test-coverage lint format check \
        shell shell-python debug clean clean-cache reset prod-build prod-up prod-down \
        prod-logs health ping env-check backup docs quick-start