from __future__ import annotations

from functools import lru_cache

from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="ADDON_",
        env_file=("../.env", ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    host: str = "0.0.0.0"
    port: int = 7000
    log_level: str = "info"

    health_base_url: AnyHttpUrl = AnyHttpUrl("http://localhost:8080")
    public_base_url: AnyHttpUrl = AnyHttpUrl("http://localhost:7000")
    cache_ttl_seconds: int = 45


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
