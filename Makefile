.EXPORT_ALL_VARIABLES:

.DEFAULT_GOAL := help
help: Makefile ## Show Makefile help message
	@echo "Below shows Makefile targets"
	@grep -E '(^[a-zA-Z_-]+:.*?##.*$$)|(^##)' Makefile | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[32m%-30s\033[0m %s\n", $$1, $$2}' | sed -e 's/\[32m##/[33m/'
.PHONY: help

requirements: pyproject.toml ## Compile requirements
	uv lock
.PHONY: requirements

install-dev: ## Install dependencies and tools for development
	uv sync
	uv run pre-commit install
.PHONY: install-dev

format: ## Run formatter
	uv run ruff format
.PHONY: format

lint: format ## Run linting
	uv run pre-commit run lint --all-files
.PHONY: lint

check: format ## Run pre-commit check
	uv run pre-commit run --all-files
.PHONY: lint

run-dev: ## Run dev stack
	docker compose -f docker-compose.yml -f docker-compose.dev.yml watch
.PHONY: run-dev
