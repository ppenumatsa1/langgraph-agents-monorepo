from fastapi import FastAPI

from app.core.config import get_settings
from app.core.logging import configure_logging
from app.domain.routes.health import router as health_router
from app.domain.routes.research import router as research_router


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)

    app = FastAPI(title=settings.service_name, version=settings.service_version)
    app.include_router(health_router)
    app.include_router(research_router, prefix="/v1")
    return app


app = create_app()
