# ===== journal-starter — Minimal/Enhanced Makefile =====
# Auto-load .env if it exists (safe: pydantic ignores extras)
ifneq (,$(wildcard .env))
	include .env
	export
endif

PYTHON ?= python

.DEFAULT_GOAL := help
.PHONY: help run test cov cov-xml ci migrate current revision downgrade \
        db-up db-down db-logs format lint \
        compose-up compose-down compose-logs web-sh freeze

help: ## Show available targets
	@grep -E '^[a-zA-Z0-9_\-]+:.*?## ' $(MAKEFILE_LIST) | sed 's/:.*## /:\t/' | sort

# ---- Local (no Docker) -------------------------------------------------------

run: ## Run FastAPI app with reload (uses .env if present)
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test: ## Run tests quietly
	pytest -q

cov: ## Run tests with coverage (terminal)
	pytest --cov=app --cov-report=term-missing

cov-xml: ## Run tests with XML coverage (for CI/codecov)
	pytest --cov=app --cov-report=xml

ci: ## CI-style test run with coverage threshold
	pytest --cov=app --cov-report=xml --cov-fail-under=90

migrate: ## Apply Alembic migrations to head
	alembic upgrade head

current: ## Show current Alembic revision
	alembic current

revision: ## Create a new Alembic revision: make revision m="your message"
	@if [ -z "$(m)" ]; then echo 'Usage: make revision m="your message"'; exit 1; fi
	alembic revision -m "$(m)" --autogenerate

downgrade: ## Revert one Alembic migration step
	alembic downgrade -1

freeze: ## Lock dependencies to requirements.txt
	$(PYTHON) -m pip freeze > requirements.txt

# ---- Optional helpers for local single-container Postgres --------------------

DB_CONTAINER ?= journal-db
DB_IMAGE     ?= postgres:16
DB_PORT      ?= 5432
DB_USER      ?= postgres
DB_PASSWORD  ?= postgres
DB_NAME      ?= journal
DB_VOLUME    ?= journal-db-data

db-up: ## Start local Postgres in Docker on port $(DB_PORT)
	@docker volume create $(DB_VOLUME) >/dev/null
	docker run --name $(DB_CONTAINER) \
		-p $(DB_PORT):5432 \
		-e POSTGRES_USER=$(DB_USER) \
		-e POSTGRES_PASSWORD=$(DB_PASSWORD) \
		-e POSTGRES_DB=$(DB_NAME) \
		-v $(DB_VOLUME):/var/lib/postgresql/data \
		-d $(DB_IMAGE)

db-down: ## Stop & remove local Postgres container (keeps volume)
	- docker stop $(DB_CONTAINER)
	- docker rm $(DB_CONTAINER)

db-logs: ## Tail logs from local Postgres container
	docker logs -f $(DB_CONTAINER)

# ---- Docker Compose workflow (recommended extension) -------------------------

compose-up: ## Build and start API + DB via docker compose
	docker compose up -d --build

compose-down: ## Stop and remove compose stack
	docker compose down

compose-logs: ## Follow API logs
	docker compose logs -f web

web-sh: ## Shell into running web container
	docker compose exec web /bin/bash || docker compose exec web sh

format: ## Format code with black & isort
	$(PYTHON) -m black app tests
	$(PYTHON) -m isort app tests

lint: ## Lint with ruff
	$(PYTHON) -m ruff check app tests
