# Researcher Agent

A FastAPI + LangGraph service that performs research, drafts a response, reviews it, and returns a summary.

## Local Setup

1. Clone the repo and enter the agent folder
   - git clone https://github.com/ppenumatsa1/langgraph-agents-monorepo.git
   - cd langgraph-agents-monorepo/agents/researcher-agent

2. Create and activate a virtual environment
   - python3.11 -m venv .venv
   - source .venv/bin/activate

3. Install dependencies
   - pip install -e .

4. Create a local environment file
   - cp .env.example .env
   - Edit values in [.env](.env) as needed (see example in [.env.example](.env.example)).

5. Run the service
   - uvicorn app.main:app --reload

For Makefile-driven commands, see [Makefile](Makefile).

## Make Targets

| Target      | Description                                             |
| ----------- | ------------------------------------------------------- |
| help        | List available targets.                                 |
| run         | Run uvicorn locally.                                    |
| run-docker  | Build and run the Docker container (uses [.env](.env)). |
| stop-docker | Stop the local Docker container.                        |
| format      | Format code with black.                                 |
| lint        | Lint code with ruff.                                    |
| test        | Run tests.                                              |
| build       | Build the Docker image.                                 |
| evals       | Placeholder for evaluation runner.                      |

## Local Tests

- Unit/integration tests: python -m pytest
- Smoke test against a running server:
  - SMOKE_BASE_URL=http://localhost:8000 python -m pytest tests/test_smoke_live.py

## Endpoints

- GET /health
- POST /v1/research
- POST /v1/research/stream

## Observability Notes

- Each request gets an `X-Correlation-Id` response header (generated if missing).
- Logs include `correlation_id` for end-to-end flow tracing.
