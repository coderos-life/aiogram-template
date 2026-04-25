bot_dir := bot

.PHONY: help
help:
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z0-9_-]+:.*##/ {printf "  %-18s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.PHONY: install
install: ## Install runtime dependencies
	@poetry install --only main

.PHONY: install-dev
install-dev: ## Install all dependencies and pre-commit hooks
	@poetry install
	@poetry run pre-commit install

.PHONY: start
start: ## Start bot in long polling mode
	@poetry run python -m $(bot_dir)

.PHONY: api
api: ## Start FastAPI health/readiness app
	@poetry run uvicorn bot.api:app --host 0.0.0.0 --port 8000 --reload

.PHONY: format
format: ## Format code
	@poetry run ruff format bot tests
	@poetry run ruff check bot tests --fix

.PHONY: ruff
ruff: ## Run ruff checks without modifying files
	@poetry run ruff check bot tests
	@poetry run ruff format bot tests --check

.PHONY: mypy
mypy: ## Run mypy
	@poetry run mypy

.PHONY: lint
lint: ruff mypy ## Run all static checks

.PHONY: test
test: ## Run tests; integration tests are skipped when PostgreSQL is unavailable
	@poetry run pytest

.PHONY: test-cov
test-cov: ## Run tests with coverage
	@poetry run pytest --cov=bot --cov-report=term-missing

.PHONY: check
check: lint test ## Run lint, type-check and tests

.PHONY: migration
migration: ## Create Alembic revision: make migration message="add users"
	@poetry run alembic revision \
	  --autogenerate \
	  --rev-id $(shell poetry run python migrations/_get_next_revision_id.py) \
	  --message "$(message)"

.PHONY: migrate
migrate: ## Upgrade database to latest revision
	@poetry run alembic upgrade head

.PHONY: stamp
stamp: ## Stamp database with latest revision without running migrations
	@poetry run alembic stamp head

.PHONY: docker-build
docker-build: ## Build Docker image
	@docker compose build

.PHONY: docker-up
docker-up: ## Start bot, PostgreSQL and Redis with Docker Compose
	@docker compose up -d --build

.PHONY: docker-down
docker-down: ## Stop Docker Compose services
	@docker compose down

.PHONY: docker-migrate
docker-migrate: ## Run Alembic migrations in Docker Compose
	@docker compose --profile tools run --rm migrator

.PHONY: docker-logs
docker-logs: ## Follow Docker Compose logs
	@docker compose logs -f

.PHONY: docker-run
docker-run: docker-up ## Backward-compatible alias
