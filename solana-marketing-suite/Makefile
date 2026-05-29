# Makefile for Solana Marketing Suite
# Common commands for development, testing, and deployment

.PHONY: help install start stop restart status logs clean test lint deploy

# Default target
.DEFAULT_GOAL := help

# Variables
NODE := node
NPM := npm
PM2 := pm2
DOCKER := docker
DOCKER_COMPOSE := docker-compose

# Directories
LOGS_DIR := logs
DATA_DIR := data
CONFIG_DIR := config
CACHE_DIR := cache

# Colors
GREEN := \033[0;32m
RED := \033[0;31m
YELLOW := \033[1;33m
BLUE := \033[0;34m
NC := \033[0m

## Help
help: ## Show this help message
	@echo "$(BLUE)Solana AI Marketing Suite - Available Commands$(NC)"
	@echo ""
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""

## Installation
install: ## Install dependencies
	@echo "$(YELLOW)Installing dependencies...$(NC)"
	$(NPM) install
	@echo "$(GREEN)✓ Dependencies installed$(NC)"

setup: install ## Full setup (install + create directories)
	@echo "$(YELLOW)Creating directories...$(NC)"
	@mkdir -p $(LOGS_DIR) $(DATA_DIR) $(CONFIG_DIR) $(CACHE_DIR)
	@echo "$(GREEN)✓ Setup complete$(NC)"

## Development
start: ## Start all agents in background
	@echo "$(YELLOW)Starting all agents...$(NC)"
	./start-all-agents.sh

start-foreground: ## Start all agents in foreground
	@echo "$(YELLOW)Starting all agents in foreground...$(NC)"
	./start-all-agents.sh --foreground

stop: ## Stop all agents
	@echo "$(YELLOW)Stopping all agents...$(NC)"
	./start-all-agents.sh stop
	@echo "$(GREEN)✓ All agents stopped$(NC)"

restart: stop start ## Restart all agents
	@echo "$(GREEN)✓ All agents restarted$(NC)"

status: ## Check status of all agents
	@./scripts/status-check.sh

## Individual Agents
start-airdrop: ## Start Airdrop Agent
	$(NODE) scripts/agent-airdrop.js start

start-community: ## Start Community Agent
	$(NODE) scripts/agent-community.js start

start-analytics: ## Start Analytics Agent
	$(NODE) scripts/agent-analytics.js server --port 3000

start-influencer: ## Start Influencer Agent
	$(NODE) scripts/agent-influencer.js start

start-nft: ## Start NFT Agent
	$(NODE) scripts/agent-nft.js start

start-quest: ## Start Quest Agent
	$(NODE) scripts/agent-quest.js start

start-content: ## Start Content Agent
	$(NODE) scripts/agent-content.js start

## Logs
logs: ## View all logs
	@tail -f $(LOGS_DIR)/*.log

logs-airdrop: ## View Airdrop Agent logs
	@tail -f $(LOGS_DIR)/agent-airdrop.log

logs-community: ## View Community Agent logs
	@tail -f $(LOGS_DIR)/agent-community.log

logs-analytics: ## View Analytics Agent logs
	@tail -f $(LOGS_DIR)/agent-analytics.log

logs-influencer: ## View Influencer Agent logs
	@tail -f $(LOGS_DIR)/agent-influencer.log

logs-nft: ## View NFT Agent logs
	@tail -f $(LOGS_DIR)/agent-nft.log

logs-quest: ## View Quest Agent logs
	@tail -f $(LOGS_DIR)/agent-quest.log

logs-content: ## View Content Agent logs
	@tail -f $(LOGS_DIR)/agent-content.log

## Testing
test: ## Run tests
	@echo "$(YELLOW)Running tests...$(NC)"
	$(NPM) test

test-coverage: ## Run tests with coverage
	@echo "$(YELLOW)Running tests with coverage...$(NC)"
	$(NPM) run test:coverage

## Linting
lint: ## Run linter
	@echo "$(YELLOW)Running linter...$(NC)"
	$(NPM) run lint

lint-fix: ## Fix linting issues
	@echo "$(YELLOW)Fixing linting issues...$(NC)"
	$(NPM) run lint:fix

## Docker
docker-build: ## Build Docker images
	@echo "$(YELLOW)Building Docker images...$(NC)"
	$(DOCKER_COMPOSE) build
	@echo "$(GREEN)✓ Docker images built$(NC)"

docker-up: ## Start all services with Docker Compose
	@echo "$(YELLOW)Starting Docker services...$(NC)"
	$(DOCKER_COMPOSE) up -d
	@echo "$(GREEN)✓ Docker services started$(NC)"

docker-down: ## Stop all Docker services
	@echo "$(YELLOW)Stopping Docker services...$(NC)"
	$(DOCKER_COMPOSE) down
	@echo "$(GREEN)✓ Docker services stopped$(NC)"

docker-logs: ## View Docker logs
	$(DOCKER_COMPOSE) logs -f

docker-ps: ## Show running Docker containers
	$(DOCKER_COMPOSE) ps

docker-restart: docker-down docker-up ## Restart Docker services
	@echo "$(GREEN)✓ Docker services restarted$(NC)"

## PM2
pm2-start: ## Start all agents with PM2
	@echo "$(YELLOW)Starting agents with PM2...$(NC)"
	$(PM2) start ecosystem.config.js
	$(PM2) save

pm2-stop: ## Stop all PM2 processes
	@echo "$(YELLOW)Stopping PM2 processes...$(NC)"
	$(PM2) stop all

pm2-restart: ## Restart all PM2 processes
	@echo "$(YELLOW)Restarting PM2 processes...$(NC)"
	$(PM2) restart all

pm2-status: ## Show PM2 process status
	$(PM2) status

pm2-logs: ## View PM2 logs
	$(PM2) logs

pm2-monit: ## Open PM2 monitoring
	$(PM2) monit

## Launch
launch-30-days: ## Run 30-day launch orchestrator
	$(NODE) scripts/launch-30-days.js

launch-config: ## Create launch configuration
	@echo "$(YELLOW)Creating launch configuration...$(NC)"
	@cp config/launch-config.example.json config/launch-config.json 2>/dev/null || echo '{"startDate":"'$$(date +%Y-%m-%d)'","budget":{"airdrop":10000,"influencers":5000}}' > config/launch-config.json
	@echo "$(GREEN)✓ Launch configuration created at config/launch-config.json$(NC)"

## Utilities
clean: ## Clean logs and cache
	@echo "$(YELLOW)Cleaning logs and cache...$(NC)"
	@rm -rf $(LOGS_DIR)/* $(CACHE_DIR)/*
	@echo "$(GREEN)✓ Cleaned$(NC)"

clean-all: clean ## Clean all generated files
	@echo "$(YELLOW)Cleaning all generated files...$(NC)"
	@rm -rf node_modules $(DATA_DIR)/*
	@echo "$(GREEN)✓ All cleaned$(NC)"

reset: clean-all install ## Reset project to clean state
	@echo "$(GREEN)✓ Project reset$(NC)"

backup: ## Backup data and config
	@echo "$(YELLOW)Creating backup...$(NC)"
	@tar -czf backup_$$(date +%Y%m%d_%H%M%S).tar.gz $(DATA_DIR) $(CONFIG_DIR) 2>/dev/null || true
	@echo "$(GREEN)✓ Backup created$(NC)"

check-env: ## Check environment variables
	@echo "$(BLUE)Checking environment variables...$(NC)"
	@test -f ~/.openclaw-env && echo "$(GREEN)✓ ~/.openclaw-env exists$(NC)" || echo "$(RED)✗ ~/.openclaw-env not found$(NC)"
	@echo ""
	@echo "Required:"
	@test -n "$$SOLANA_RPC_URL" && echo "  $(GREEN)✓$(NC) SOLANA_RPC_URL" || echo "  $(RED)✗$(NC) SOLANA_RPC_URL"
	@test -n "$$SOLANA_WALLET_PRIVATE_KEY" && echo "  $(GREEN)✓$(NC) SOLANA_WALLET_PRIVATE_KEY" || echo "  $(RED)✗$(NC) SOLANA_WALLET_PRIVATE_KEY"
	@echo ""
	@echo "Optional:"
	@test -n "$$DISCORD_BOT_TOKEN" && echo "  $(GREEN)✓$(NC) DISCORD_BOT_TOKEN" || echo "  $(YELLOW)○$(NC) DISCORD_BOT_TOKEN"
	@test -n "$$TWITTER_API_KEY" && echo "  $(GREEN)✓$(NC) TWITTER_API_KEY" || echo "  $(YELLOW)○$(NC) TWITTER_API_KEY"
	@test -n "$$TELEGRAM_BOT_TOKEN" && echo "  $(GREEN)✓$(NC) TELEGRAM_BOT_TOKEN" || echo "  $(YELLOW)○$(NC) TELEGRAM_BOT_TOKEN"

## Deployment
deploy: ## Deploy to production (requires PM2)
	@echo "$(YELLOW)Deploying to production...$(NC)"
	git pull origin main
	$(NPM) install --production
	$(PM2) restart ecosystem.config.js --env production
	@echo "$(GREEN)✓ Deployed$(NC)"

deploy-staging: ## Deploy to staging
	@echo "$(YELLOW)Deploying to staging...$(NC)"
	git pull origin develop
	$(NPM) install
	$(PM2) restart ecosystem.config.js --env development
	@echo "$(GREEN)✓ Deployed to staging$(NC)"

## Monitoring
monitor: ## Open monitoring dashboard
	@echo "$(BLUE)Opening monitoring dashboard...$(NC)"
	@open http://localhost:3000/dashboard || xdg-open http://localhost:3000/dashboard

health: ## Check health of all services
	@echo "$(BLUE)Health Check$(NC)"
	@echo ""
	@curl -s http://localhost:3000/health | jq . 2>/dev/null || echo "$(YELLOW)Analytics dashboard not running$(NC)"

## Database
db-setup: ## Setup database (Docker)
	@echo "$(YELLOW)Setting up database...$(NC)"
	$(DOCKER_COMPOSE) up -d postgres redis
	@echo "$(GREEN)✓ Database ready$(NC)"

db-reset: ## Reset database
	@echo "$(YELLOW)Resetting database...$(NC)"
	$(DOCKER_COMPOSE) down -v
	$(DOCKER_COMPOSE) up -d postgres redis
	@echo "$(GREEN)✓ Database reset$(NC)"

## Quick Actions
quickstart: setup check-env start ## Quick start: setup, check env, and start
	@echo "$(GREEN)✓ Quickstart complete!$(NC)"

dev: install start-foreground ## Development mode: install and start in foreground

production: install pm2-start ## Production mode: install and start with PM2

ci: install lint test ## CI pipeline: install, lint, and test

all: setup start status ## Full setup and start