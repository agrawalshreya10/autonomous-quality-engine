"""Application settings loaded from environment and .env."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Test run configuration. Override via env vars or .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    base_url: str = Field(
        default="https://opensource-demo.orangehrmlive.com",
        description="OrangeHRM base URL (scheme, host, port, optional path). No trailing slash.",
    )
    ignore_https_errors: bool = Field(
        default=False,
        description="If true, ignore TLS certificate errors (e.g. self-signed HTTPS on localhost). Default false for safe validation; do not enable against production.",
    )
    browser: Literal["chromium", "firefox", "webkit"] = Field(
        default="chromium",
        description="Browser to run tests in",
    )
    headless: bool = Field(default=True, description="Run browser headless")
    timeout_ms: int = Field(default=15_000, description="Default timeout in milliseconds")
    slow_mo_ms: int = Field(default=0, description="Slow down operations by N ms")
    # Credentials (optional; demo defaults)
    orangehrm_user: str = Field(default="Admin", description="Login username")
    orangehrm_password: str = Field(default="admin123", description="Login password")

    @field_validator("base_url", mode="before")
    @classmethod
    def normalize_base_url(cls, v: object) -> str:
        s = v.strip().rstrip("/") if isinstance(v, str) else str(v).strip().rstrip("/")
        return s


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance."""
    return Settings()
