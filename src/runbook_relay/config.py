from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from RUNBOOK_RELAY_* environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="RUNBOOK_RELAY_",
        extra="ignore",
    )

    service_name: str = "Runbook Relay"
    environment: str = "development"
    api_key: SecretStr = Field(..., min_length=1)
    database_url: SecretStr = Field(..., min_length=1)
    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    # Required values are supplied by pydantic-settings from the environment.
    return Settings()  # type: ignore[call-arg]
