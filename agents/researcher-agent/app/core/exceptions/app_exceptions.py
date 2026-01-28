from __future__ import annotations


class ResearcherAgentError(Exception):
    """Base exception for the researcher agent."""

    status_code = 500
    code = "agent_error"

    def __init__(
        self, message: str = "Unexpected error", *, cause: Exception | None = None
    ) -> None:
        super().__init__(message)
        self.message = message
        self.cause = cause

    def to_dict(self) -> dict[str, str]:
        return {"code": self.code, "message": self.message}


class ExternalServiceError(ResearcherAgentError):
    """Raised when external services (LLM/search) fail."""

    status_code = 502
    code = "external_service_error"


class BadRequestError(ResearcherAgentError):
    """Raised for invalid inputs or unsupported requests."""

    status_code = 400
    code = "bad_request"


class UpstreamTimeoutError(ResearcherAgentError):
    """Raised when an upstream dependency times out."""

    status_code = 504
    code = "upstream_timeout"
