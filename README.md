# LangGraph Agents Monorepo

## Summary

Monorepo for LangGraph-based agents deployed to Azure Container Apps with azd. Each agent is an independently deployable FastAPI service following the same layered architecture and observability patterns.

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

## Prerequisites (Ubuntu/Debian)

Install the required tools on Ubuntu/Debian:

1. Update packages
   - sudo apt-get update
2. Install Python 3.11 and venv
   - sudo apt-get install -y python3.11 python3.11-venv python3-pip
3. Install Docker (for container builds)
   - sudo apt-get install -y docker.io
4. Install Azure CLI
   - curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
5. Install Azure Developer CLI (azd)
   - curl -fsSL https://aka.ms/install-azd.sh | sudo bash
6. Install Make (optional)
   - sudo apt-get install -y make

## Local Development

See [agents/researcher-agent/README.md](agents/researcher-agent/README.md) for local setup and run instructions.

## Verify Local Deployment

Run the smoke tests against a local server:

- SMOKE_BASE_URL=http://localhost:8000 python -m pytest agents/researcher-agent/tests/test_smoke_live.py

## Azure Deployment (azd)

We use azd for deployments. Before running azd, ensure:

- A Python virtual environment is created and active for the agent (for local validation)
- Agent-level .env is present with required configuration

Typical steps:

1. azd auth login
2. azd env new
3. azd provision
4. azd deploy

## Verify Azure Deployment

Run the smoke tests against the deployed endpoint:

- SMOKE_BASE_URL=https://<your-app>.azurecontainerapps.io python -m pytest agents/researcher-agent/tests/test_smoke_live.py

## Observability

- Structured logging with trace/span correlation
- OpenTelemetry export to Application Insights
- LangGraph spans for agent execution
- Tool execution spans (ToolNode-based tools appear as dependencies)

## Agent Design Docs

Each agent owns design artifacts under docs/design (PRD, tech stack, project structure, user flow).

| Agent            | Description                        | README                                                                 |
| ---------------- | ---------------------------------- | ---------------------------------------------------------------------- |
| researcher-agent | Research → write → review workflow | [agents/researcher-agent/README.md](agents/researcher-agent/README.md) |

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

## Disclaimer

This repository is provided for educational and demonstration purposes only. It is not intended for production use as-is. You are responsible for reviewing, testing, and securing any code, configurations, credentials, or deployment artifacts before using them in real systems. Do not deploy this repository without your own security review, compliance checks, and operational hardening (logging, alerting, backups, access controls, and cost safeguards). By using this repository, you acknowledge that you assume all risks associated with its use.
