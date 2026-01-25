from dataclasses import dataclass, field


@dataclass
class ResearchState:
    topic: str
    audience: str | None
    tone: str | None
    length: str | None
    time_range: str | None
    sources: list[dict[str, str]] = field(default_factory=list)
    research_summary: str = ""
    draft: str = ""
    review_notes: list[str] = field(default_factory=list)
    summary: str = ""
