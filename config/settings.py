"""Application settings loaded from environment and .env."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Test run configuration. Override via env vars or .env (see config/env.example).

    Local self-signed HTTPS (MAMP, ohrm.test): set IGNORE_HTTPS_ERRORS=true in .env; the
    default here is false so public demo/CI get full certificate validation.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    base_url: str = Field(
        default="https://opensource-demo.orangehrmlive.com",
        description="OrangeHRM base URL (scheme, host, port, optional path). No trailing slash.",
    )
    # Default False: validate TLS (public demo, CI). **Migration:** the field previously defaulted
    # to True; if your local SUT is HTTPS with a self-signed or dev-only cert (MAMP, ohrm.test,
    # https://localhost), set IGNORE_HTTPS_ERRORS=true in .env. See config/env.example.
    ignore_https_errors: bool = Field(
        default=False,
        description=(
            "If true, Playwright ignores TLS certificate errors for the SUT origin. "
            "Default false for full certificate validation. "
            "Local self-signed HTTPS (MAMP, https://ohrm.test, dev localhost) requires true — set "
            "IGNORE_HTTPS_ERRORS in .env; never use against production. "
            "See config/env.example."
        ),
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
