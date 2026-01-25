# Researcher Agent User Flow

## Primary Flow

1. User submits a topic.
2. System performs research and gathers sources.
3. System drafts a response.
4. System reviews the draft for accuracy and clarity.
5. System returns a concise summary.

## Inputs

- Topic (required)
- Constraints: audience, tone, length, time range (optional)

## Outputs

- Draft response
- Review notes
- Final summary

## Error Handling

- Missing topic → validation error
- Low-confidence research → return partial summary with warning

## Technical Flow (Request → Response)

1. HTTP request hits FastAPI route: [agents/researcher-agent/app/domain/routes/research.py](agents/researcher-agent/app/domain/routes/research.py)
2. Route creates `ResearchState` and calls service: [agents/researcher-agent/app/domain/services/research_service.py](agents/researcher-agent/app/domain/services/research_service.py)
3. Service builds LangGraph and invokes workflow: [agents/researcher-agent/app/langgraph/graph.py](agents/researcher-agent/app/langgraph/graph.py)
4. Researcher node enriches state via repo + LLM:
   - Repo: [agents/researcher-agent/app/domain/repo/web_search_repo.py](agents/researcher-agent/app/domain/repo/web_search_repo.py)
   - Tool: [agents/researcher-agent/app/langgraph/tools/web_search.py](agents/researcher-agent/app/langgraph/tools/web_search.py)
   - LLM client: [agents/researcher-agent/app/core/llm.py](agents/researcher-agent/app/core/llm.py)
   - Prompt: [agents/researcher-agent/app/langgraph/prompts/researcher.py](agents/researcher-agent/app/langgraph/prompts/researcher.py)
5. Writer node drafts response with LLM: [agents/researcher-agent/app/langgraph/nodes/writer.py](agents/researcher-agent/app/langgraph/nodes/writer.py)
6. Reviewer node produces review notes and summary: [agents/researcher-agent/app/langgraph/nodes/reviewer.py](agents/researcher-agent/app/langgraph/nodes/reviewer.py)
7. Final state returned to route and serialized into response model: [agents/researcher-agent/app/domain/schemas/research.py](agents/researcher-agent/app/domain/schemas/research.py)
