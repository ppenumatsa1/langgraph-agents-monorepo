from __future__ import annotations

import logging
from functools import lru_cache

from azure.identity import DefaultAzureCredential
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import AzureChatOpenAI

from app.core.exceptions import ExternalServiceError
from app.core.utils import get_settings

logger = logging.getLogger(__name__)


async def chat_completion(system_prompt: str, user_prompt: str) -> str:
    model = _get_model()
    if model is None:
        logger.warning("LLM config missing; returning placeholder response.")
        return ""

    try:
        response = await model.ainvoke(
            [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt),
            ]
        )
        return (response.content or "").strip()
    except Exception as exc:
        raise ExternalServiceError("LLM request failed", cause=exc) from exc


@lru_cache
def _get_model() -> AzureChatOpenAI | None:
    settings = get_settings()
    if not settings.azure_openai_endpoint or not settings.azure_openai_deployment_name:
        return None

    credential = DefaultAzureCredential()
    return AzureChatOpenAI(
        azure_endpoint=settings.azure_openai_endpoint,
        azure_deployment=settings.azure_openai_deployment_name,
        openai_api_version=settings.azure_openai_api_version,
        azure_ad_token_provider=lambda: credential.get_token(
            "https://cognitiveservices.azure.com/.default"
        ).token,
    )
