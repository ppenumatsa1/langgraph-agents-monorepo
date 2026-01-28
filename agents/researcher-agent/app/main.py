import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.exceptions import ResearcherAgentError
from app.core.logging import configure_logging
from app.core.middleware.correlation import CorrelationIdMiddleware
from app.core.observability import configure_telemetry
from app.core.utils import get_settings
from app.domain.routes.health import router as health_router
from app.domain.routes.research import router as research_router


def _configure_exception_handlers(app: FastAPI) -> None:
    logger = logging.getLogger("app.exceptions")

    @app.exception_handler(ResearcherAgentError)
    async def handle_agent_error(request: Request, exc: ResearcherAgentError) -> JSONResponse:
        logger.warning("Agent error: %s", exc, extra={"path": request.url.path})
        return JSONResponse(status_code=exc.status_code, content={"error": exc.to_dict()})

    @app.exception_handler(Exception)
    async def handle_unhandled_error(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled error", extra={"path": request.url.path})
        return JSONResponse(
            status_code=500,
            content={"error": {"code": "internal_error", "message": "Internal server error"}},
        )


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)

    app = FastAPI(title=settings.service_name, version=settings.service_version)
    app.add_middleware(CorrelationIdMiddleware)
    configure_telemetry(app)
    _configure_exception_handlers(app)
    app.include_router(health_router)
    app.include_router(research_router, prefix="/v1")
    return app


app = create_app()
