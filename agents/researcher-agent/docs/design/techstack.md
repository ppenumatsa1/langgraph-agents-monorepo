# Researcher Agent Tech Stack

## Runtime
- Python (latest stable)
- FastAPI
- LangGraph

## Observability
- OpenTelemetry instrumentation

## Hosting (planned)
- Azure Container Apps
- Azure Container Registry
- Azure Key Vault (secrets storage, injected into ACA as secrets)

## CI/Quality (planned)
- Linting and formatting
- Unit tests
- Basic smoke tests

## Local Development
- Containerized workflow using Docker
- Environment variables only (no .env in containers)
