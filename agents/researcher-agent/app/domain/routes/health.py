import logging

from fastapi import APIRouter

router = APIRouter()
logger = logging.getLogger("app.routes.health")


@router.get("/health")
def health() -> dict:
    logger.info("Health check invoked")
    return {"status": "ok"}
