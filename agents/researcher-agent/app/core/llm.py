from __future__ import annotations

import logging
from functools import lru_cache

from azure.identity import DefaultAzureCredential
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import AzureChatOpenAI
from opentelemetry import trace

from app.core.exceptions import ExternalServiceError
from app.core.utils import get_settings

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)


async def chat_completion(system_prompt: str, user_prompt: str, config: dict | None = None) -> str:
    model = _get_model()
    if model is None:
        logger.warning("LLM config missing; returning placeholder response.")
        return ""

    try:
        with tracer.start_as_current_span("llm.chat_completion") as span:
            span.set_attribute("app.prompt.system_length", len(system_prompt))
            span.set_attribute("app.prompt.user_length", len(user_prompt))
            logger.info("LLM request started")
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt),
            ]
            if config is None:
                response = await model.ainvoke(messages)
            else:
                response = await model.ainvoke(messages, config=config)
            logger.info("LLM request completed")
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
