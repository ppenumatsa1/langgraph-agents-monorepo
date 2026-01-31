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
4. Researcher node fetches sources via enrichment:
   - Enrichment: [agents/researcher-agent/app/domain/services/research_enrichment.py](agents/researcher-agent/app/domain/services/research_enrichment.py)
   - ToolNode executes web search tool with message-based tool calls
   - Tool: [agents/researcher-agent/app/langgraph/tools/web_search.py](agents/researcher-agent/app/langgraph/tools/web_search.py)
5. Researcher node summarizes sources with the LLM:
   - LLM client: [agents/researcher-agent/app/core/llm.py](agents/researcher-agent/app/core/llm.py)
   - Prompt: [agents/researcher-agent/app/langgraph/prompts/researcher.py](agents/researcher-agent/app/langgraph/prompts/researcher.py)
6. Writer node drafts response with LLM: [agents/researcher-agent/app/langgraph/nodes/writer.py](agents/researcher-agent/app/langgraph/nodes/writer.py)
7. Reviewer node produces review notes and summary: [agents/researcher-agent/app/langgraph/nodes/reviewer.py](agents/researcher-agent/app/langgraph/nodes/reviewer.py)
8. Final state returned to route and serialized into response model: [agents/researcher-agent/app/domain/schemas/research.py](agents/researcher-agent/app/domain/schemas/research.py)

Note: Tool-call tracing depends on using the LangChain tool wrapper (not the direct function) and passing `config` with callbacks through the call chain.
