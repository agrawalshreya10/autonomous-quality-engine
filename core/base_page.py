"""Base page with common actions and waits for all page objects."""

from pathlib import Path
from typing import Any

from playwright.sync_api import Locator, Page

from config.settings import Settings


class BasePage:
    """Base class for all page objects. Wraps Playwright Page with config and helpers."""

    def __init__(self, page: Page, settings: Settings, path: str = "") -> None:
        self._page = page
        self._settings = settings
        self._path = path.strip("/")

    @property
    def page(self) -> Page:
        return self._page

    @property
    def base_url(self) -> str:
        return self._settings.base_url.rstrip("/")

    def navigate(self, path: str = "") -> None:
        """Navigate to base_url + path. Path can start with / or be relative."""
        p = path.strip("/") if path else self._path
        url = f"{self.base_url}/{p}" if p else self.base_url
        self._page.goto(url, wait_until="domcontentloaded")

    def click(self, locator: Locator | str, **kwargs: Any) -> None:
        el = self._page.locator(locator) if isinstance(locator, str) else locator
        el.click(**kwargs)

    def fill(self, locator: Locator | str, value: str, **kwargs: Any) -> None:
        el = self._page.locator(locator) if isinstance(locator, str) else locator
        el.fill(value, **kwargs)

    def get_text(self, locator: Locator | str) -> str:
        el = self._page.locator(locator) if isinstance(locator, str) else locator
        return el.inner_text()

    def wait_for_visible(self, locator: Locator | str, timeout_ms: int | None = None) -> None:
        el = self._page.locator(locator) if isinstance(locator, str) else locator
        el.wait_for(state="visible", timeout=timeout_ms or self._settings.timeout_ms)

    def wait_for_load_state(self, state: str = "networkidle") -> None:
        self._page.wait_for_load_state(state)

    def wait_for_url(self, pattern: str | None = None, timeout_ms: int | None = None) -> None:
        self._page.wait_for_url(url=pattern, timeout=timeout_ms or self._settings.timeout_ms)

    def screenshot(self, name: str, path: str | Path | None = None) -> bytes:
        out = path or f"reports/screenshots/{name}.png"
        return self._page.screenshot(path=out)

    def is_visible(self, locator: Locator | str) -> bool:
        el = self._page.locator(locator) if isinstance(locator, str) else locator
        return el.is_visible()
