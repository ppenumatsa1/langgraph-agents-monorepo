from functools import lru_cache

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="RA_", case_sensitive=False)

    service_name: str = "researcher-agent"
    service_version: str = "0.1.0"
    log_level: str = "INFO"

    azure_openai_endpoint: str | None = Field(
        default=None,
        validation_alias="AZURE_OPENAI_ENDPOINT",
    )
    azure_openai_deployment_name: str | None = Field(
        default=None,
        validation_alias="AZURE_OPENAI_DEPLOYMENT_NAME",
    )
    azure_openai_api_version: str | None = Field(
        default="2024-12-01-preview",
        validation_alias="AZURE_OPENAI_API_VERSION",
    )


@lru_cache
def get_settings() -> Settings:
    load_dotenv()
    return Settings()
