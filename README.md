# LangGraph Agents Monorepo

Production-ready monorepo for LangGraph agents deployed on Azure Container Apps (ACA) with azd. Each agent is independently deployable as a FastAPI service and follows a consistent, layered architecture.

## Goals
- One deployable service per agent
- LangGraph-first workflow modeling
- No shared runtime Python code across agents
- Azure-ready from day one (ACA + ACR + App Insights)
- Environment-driven configuration (12-factor)

## What’s Included
- Agent-local FastAPI app with layered architecture (routes → services → repo → core)
- LangGraph workflows per agent with nodes, tools, and prompts
- Structured logging + OpenTelemetry-ready hooks
- Dockerfile per agent for containerized runs
- Root Makefile to orchestrate agent tasks

## Repository Structure
- agents/ — independently deployable agents
- docs/ — cross-agent docs and index
- infra/ — shared Azure infra (planned)

See the agents index at [docs/agents/README.md](docs/agents/README.md).

## Prerequisites
- Python 3.11+
- Docker (for container builds)
- Azure CLI and Azure Developer CLI (for Azure deployments)
- Make (optional but recommended)

## Agent Design Docs
Each agent owns its design artifacts under docs/design (PRD, tech stack, project structure, user flow).

| Agent | Description | README |
| --- | --- | --- |
| researcher-agent | Research → write → review workflow | [agents/researcher-agent/README.md](agents/researcher-agent/README.md) |

## Local Development (Agent)
1. Create venv and install dependencies
2. Configure env vars in agent .env
3. Run the agent via uvicorn or Makefile

## Common Make Targets
Root orchestrates per-agent tasks:
- make run AGENT=<agent>
- make test AGENT=<agent>
- make build AGENT=<agent>

Each agent also supports local targets in its Makefile.

## Azure Deployment (azd)
- One azd project, multiple services
- One ACA environment, one container app per agent
- Shared infra provisioned once

## Observability
- Structured logging by default
- OpenTelemetry hooks ready for App Insights

## Status
The monorepo is production-ready in structure, with one working agent (researcher) and additional agents expected to follow the same blueprint.
