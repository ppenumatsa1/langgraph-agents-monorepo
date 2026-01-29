# Researcher Agent PRD

## Purpose

Provide a focused research workflow that takes a topic, gathers sources, drafts a response, reviews for accuracy, and returns a concise summary. This agent does not publish or distribute content.

## Scope

- Topic intake
- Research + source collection
- Draft writing
- Self-review
- Final summary

## Users

- Internal teams needing quick research briefs
- Developers testing LangGraph workflows

## Inputs

- Topic (string)
- Optional constraints: length, tone, audience, time range

## Outputs

- Research summary
- Draft response
- Review notes
- Final concise summary

## Functional Requirements

1. Accept a topic and optional constraints.
2. Research and cite sources internally.
3. Produce a draft response.
4. Review for accuracy, completeness, and clarity.
5. Return a final summary.

## Non-Goals

- No publishing to external systems
- No long-form report generation beyond summary
- No agent-to-agent calls unless explicitly designed

## Design Notes

- Web search is executed via a LangGraph ToolNode (not a plain function call) so tool calls are captured as trace spans in Azure Application Insights.

## Quality Gates

### Artifact Completion Checklist

- [ ] prd.md complete with scope, inputs, outputs, requirements
- [ ] projectstructure.md describes final agent layout
- [ ] techstack.md lists runtime, libraries, hosting
- [ ] userflow.md captures the user journey

### Code Compile/Test/Validation Checklist (for later phases)

- [ ] Dependency lock file present
- [ ] Service starts locally without errors
- [ ] Unit tests cover core workflow nodes
- [ ] Linting and formatting pass
- [ ] Basic smoke test runs against FastAPI endpoint
- [ ] Tracing spans emitted for each node

## Risks

- Source quality variance
- Hallucination risk in summaries

## Milestones

- Phase 1: Design artifacts complete
- Phase 2: Code scaffolding complete
- Phase 3: Infra and deployment ready

## Open Questions

- Final evaluation criteria for summary accuracy
- Required minimum citations
