from pydantic import BaseModel, Field


class ResearchRequest(BaseModel):
    topic: str = Field(..., min_length=3)
    audience: str | None = None
    tone: str | None = None
    length: str | None = None
    time_range: str | None = None


class ResearchResponse(BaseModel):
    topic: str
    draft: str
    review_notes: list[str]
    summary: str
