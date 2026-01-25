# Researcher Agent

A FastAPI + LangGraph service that performs research, drafts a response, reviews it, and returns a summary.

## Local Run
- Install dependencies
- Start server: uvicorn app.main:app --reload

## Endpoints
- GET /health
- POST /v1/research
