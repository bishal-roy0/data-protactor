from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables."""

    app_name: str = "Karna"
    environment: str = "development"
    log_level: str = "INFO"
    openai_api_key: str | None = None
    openai_vision_model: str = "gpt-4.1-mini"
    virustotal_api_key: str | None = None
    android_app_download_url: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings for the current process."""

    return Settings()
