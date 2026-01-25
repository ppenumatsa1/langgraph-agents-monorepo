IMAGE ?= researcher-agent
PORT ?= 8000
CONTAINER_NAME ?= researcher-agent-local

.PHONY: help
help:
	@echo "Targets:"
	@echo "  run           - Run uvicorn locally"
	@echo "  run-docker    - Build and run Docker container"
	@echo "  stop-docker   - Stop Docker container"
	@echo "  format        - Format code with black"
	@echo "  lint          - Lint code with ruff"
	@echo "  test          - Run tests"
	@echo "  build         - Build Docker image"
	@echo "  evals         - Run evaluations (placeholder)"

run:
	uvicorn app.main:app --reload

run-docker:
	docker build -t $(IMAGE) .
	docker run --rm --name $(CONTAINER_NAME) -p $(PORT):8000 --env-file .env $(IMAGE)

stop-docker:
	@docker rm -f $(CONTAINER_NAME) >/dev/null 2>&1 || true

format:
	black app tests

lint:
	ruff check app tests

test:
	pytest

evals:
	@echo "evals: add evaluation runner"

build:
	docker build -t $(IMAGE) .
