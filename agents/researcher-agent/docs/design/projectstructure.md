# Researcher Agent Project Structure

This agent is a single FastAPI service with LangGraph workflows and agent-local modules only.

```text
agents/researcher-agent/
├── app/
│   ├── main.py
│   ├── core/
│   │   ├── config.py
│   │   ├── logging.py
│   │   ├── telemetry.py
│   │   └── exceptions.py
│   ├── domain/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── routes/
│   └── langgraph/
│       ├── graph.py
│       ├── state.py
│       ├── tools.py
│       └── nodes/
│           ├── researcher.py
│           ├── writer.py
│           └── reviewer.py
├── docs/
│   └── design/
│       ├── prd.md
│       ├── projectstructure.md
│       ├── techstack.md
│       └── userflow.md
├── tests/
├── Dockerfile
├── pyproject.toml
└── README.md
```

Notes:
- docs/design is agent-level and is the source of truth for design artifacts.
- Root docs will only index and link to each agent’s design docs.
