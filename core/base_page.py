"""Base page with common actions and waits for all page objects."""

from pathlib import Path
from typing import Any

from playwright.sync_api import Locator, Page, expect

from config.settings import Settings
from utils.helpers import truncate_for_log
from utils.logger import get_interaction_logger, log_interaction


class BasePage:
    """Base class for all page objects. Wraps Playwright Page with config and helpers."""

    def __init__(self, page: Page, settings: Settings, path: str = "") -> None:
        self._page = page
        self._settings = settings
        self._path = path.strip("/")
        self._interaction_log = get_interaction_logger(self.__class__.__name__)

    @property
    def page(self) -> Page:
        return self._page

    @property
    def base_url(self) -> str:
        return self._settings.base_url.rstrip("/")

    def get_resilient_locator(self, primary_selector: str, fallback_selector: str) -> Locator:
        """
        Self-healing locator: match primary selector, or fallback if the DOM differs
        (e.g. MAMP / ohrm.test vs hosted demo).
        """
        return self._page.locator(primary_selector).or_(self._page.locator(fallback_selector))

    @staticmethod
    def _resolve_locator(page: Page, locator: Locator | str) -> Locator:
        return page.locator(locator) if isinstance(locator, str) else locator

    def _element_label(
        self,
        locator: Locator | str,
        element_label: str | None,
    ) -> str:
        if element_label:
            return element_label
        if isinstance(locator, str):
            return truncate_for_log(locator)
        return "locator"

    def navigate(self, path: str = "") -> None:
        """Navigate to base_url + path. Path can start with / or be relative."""
        p = path.strip("/") if path else self._path
        url = f"{self.base_url}/{p}" if p else self.base_url
        log_interaction(self._interaction_log, "navigate", truncate_for_log(url))
        self._page.goto(url, wait_until="domcontentloaded")

    def click(
        self,
        locator: Locator | str,
        *,
        element_label: str | None = None,
        **kwargs: Any,
    ) -> None:
        el = self._resolve_locator(self._page, locator)
        label = self._element_label(locator, element_label)
        log_interaction(self._interaction_log, "click", label)
        timeout = self._settings.timeout_ms
        expect(el).to_be_visible(timeout=timeout)
        expect(el).to_be_enabled(timeout=timeout)
        el.click(**kwargs)

    def fill(
        self,
        locator: Locator | str,
        value: str,
        *,
        element_label: str | None = None,
        **kwargs: Any,
    ) -> None:
        el = self._resolve_locator(self._page, locator)
        label = self._element_label(locator, element_label)
        log_interaction(self._interaction_log, "fill", label)
        timeout = self._settings.timeout_ms
        expect(el).to_be_visible(timeout=timeout)
        expect(el).to_be_editable(timeout=timeout)
        el.fill(value, **kwargs)

    def get_text(self, locator: Locator | str) -> str:
        el = self._resolve_locator(self._page, locator)
        return el.inner_text()

    def wait_for_visible(self, locator: Locator | str, timeout_ms: int | None = None) -> None:
        el = self._resolve_locator(self._page, locator)
        el.wait_for(state="visible", timeout=timeout_ms or self._settings.timeout_ms)

    def wait_for_load_state(self, state: str = "networkidle") -> None:
        self._page.wait_for_load_state(state)

    def wait_for_url(self, pattern: str | None = None, timeout_ms: int | None = None) -> None:
        self._page.wait_for_url(url=pattern, timeout=timeout_ms or self._settings.timeout_ms)

    def screenshot(self, name: str, path: str | Path | None = None) -> bytes:
        out = path or f"reports/screenshots/{name}.png"
        return self._page.screenshot(path=out)

    def is_visible(self, locator: Locator | str) -> bool:
        el = self._resolve_locator(self._page, locator)
        return el.is_visible()
