"""Base page with common actions and waits for all page objects."""

from collections.abc import Callable
from pathlib import Path
from typing import Any, TypeVar

from playwright.sync_api import Locator, Page, expect

from config.settings import Settings
from utils.helpers import truncate_for_log
from utils.logger import (
    get_interaction_logger,
    get_logger,
    log_interaction_result,
    log_interaction_start,
)

T = TypeVar("T")


class BasePage:
    """Base class for all page objects. Wraps Playwright Page with config and helpers."""

    def __init__(self, page: Page, settings: Settings, path: str = "") -> None:
        self._page = page
        self._settings = settings
        self._path = path.strip("/")
        self._interaction_log = get_interaction_logger(self.__class__.__name__)
        self._error_logger = get_logger(f"page.{self.__class__.__name__}")

    def _run(self, action: str, context: str, fn: Callable[[], T]) -> T:
        """Run a page action; on failure log the error with traceback and re-raise (.cursorrules)."""
        try:
            return fn()
        except Exception:
            self._error_logger.exception(
                "Failed during %s on %s",
                action,
                context,
            )
            raise

    def _run_logged(self, action: str, context: str, fn: Callable[[], T]) -> T:
        """Log start and truthful outcome around an action execution."""
        log_interaction_start(self._interaction_log, action, context)
        try:
            result = self._run(action, context, fn)
            log_interaction_result(self._interaction_log, action, context, success=True)
            return result
        except Exception:
            log_interaction_result(self._interaction_log, action, context, success=False)
            raise

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
        ctx = f"{truncate_for_log(primary_selector)} | {truncate_for_log(fallback_selector)}"

        def _build() -> Locator:
            return self._page.locator(primary_selector).or_(self._page.locator(fallback_selector))

        return self._run("get_resilient_locator", ctx, _build)

    def get_resilient_role_button(self, name: str, fallback_selector: str) -> Locator:
        """Critical path: role button + CSS/text fallback (.or_ pattern)."""
        ctx = f'button[name="{name}"] | {truncate_for_log(fallback_selector)}'

        def _build() -> Locator:
            return self._page.get_by_role("button", name=name).or_(self._page.locator(fallback_selector))

        return self._run("get_resilient_locator", ctx, _build)

    def get_resilient_role_menuitem(self, name: str, fallback_selector: str) -> Locator:
        """Critical path: role menuitem + CSS fallback (.or_ pattern)."""
        ctx = f'menuitem[name="{name}"] | {truncate_for_log(fallback_selector)}'

        def _build() -> Locator:
            return self._page.get_by_role("menuitem", name=name).or_(self._page.locator(fallback_selector))

        return self._run("get_resilient_locator", ctx, _build)

    def get_resilient_placeholder(self, primary_placeholder: str, fallback_placeholder: str) -> Locator:
        """Two placeholder variants (e.g. search hints on different builds)."""
        ctx = f"placeholder | {truncate_for_log(primary_placeholder)} | {truncate_for_log(fallback_placeholder)}"

        def _build() -> Locator:
            return self._page.get_by_placeholder(primary_placeholder).or_(
                self._page.get_by_placeholder(fallback_placeholder)
            ).first

        return self._run("get_resilient_locator", ctx, _build)

    @staticmethod
    def _resolve_locator(page: Page, locator: Locator | str) -> Locator:
        return page.locator(locator) if isinstance(locator, str) else locator

    def navigate(self, path: str = "") -> None:
        """Navigate to base_url + path. Path can start with / or be relative."""
        p = path.strip("/") if path else self._path
        url = f"{self.base_url}/{p}" if p else self.base_url

        def _goto() -> None:
            self._page.goto(url, wait_until="domcontentloaded")

        self._run_logged("navigate", truncate_for_log(url), _goto)

    def click(
        self,
        locator: Locator | str,
        *,
        element_label: str,
        **kwargs: Any,
    ) -> None:
        el = self._resolve_locator(self._page, locator)
        timeout = self._settings.timeout_ms

        def _click() -> None:
            expect(el).to_be_visible(timeout=timeout)
            expect(el).to_be_enabled(timeout=timeout)
            el.click(**kwargs)

        self._run_logged("click", element_label, _click)

    def fill(
        self,
        locator: Locator | str,
        value: str,
        *,
        element_label: str,
        **kwargs: Any,
    ) -> None:
        el = self._resolve_locator(self._page, locator)
        timeout = self._settings.timeout_ms

        def _fill() -> None:
            expect(el).to_be_visible(timeout=timeout)
            expect(el).to_be_editable(timeout=timeout)
            el.fill(value, **kwargs)

        self._run_logged("fill", element_label, _fill)

    def get_text(self, locator: Locator | str, *, element_label: str) -> str:
        el = self._resolve_locator(self._page, locator)

        def _text() -> str:
            return el.inner_text()

        return self._run("get_text", element_label, _text)

    def wait_for_visible(self, locator: Locator | str, *, element_label: str, timeout_ms: int | None = None) -> None:
        el = self._resolve_locator(self._page, locator)
        t = timeout_ms or self._settings.timeout_ms

        def _wait() -> None:
            el.wait_for(state="visible", timeout=t)

        self._run("wait_for_visible", element_label, _wait)

    def wait_for_load_state(self, state: str = "networkidle") -> None:
        def _wait() -> None:
            self._page.wait_for_load_state(state)

        self._run("wait_for_load_state", state, _wait)

    def wait_for_url(self, pattern: str | None = None, timeout_ms: int | None = None) -> None:
        ctx = pattern or ""

        def _wait() -> None:
            self._page.wait_for_url(url=pattern, timeout=timeout_ms or self._settings.timeout_ms)

        self._run("wait_for_url", ctx, _wait)

    def screenshot(self, name: str, path: str | Path | None = None) -> bytes:
        out = path or f"reports/screenshots/{name}.png"

        def _shot() -> bytes:
            return self._page.screenshot(path=out)

        return self._run("screenshot", str(name), _shot)

    def is_visible(self, locator: Locator | str, *, element_label: str) -> bool:
        el = self._resolve_locator(self._page, locator)

        def _vis() -> bool:
            return el.is_visible()

        return self._run("is_visible", element_label, _vis)

    def count_locator_matches(self, selector: str, *, element_label: str) -> int:
        """Count elements matching a selector (e.g. table rows)."""

        def _count() -> int:
            return self._page.locator(selector).count()

        return self._run("locator_count", element_label, _count)

    def locator_nth(self, selector: str, index: int, *, element_label: str) -> Locator:
        """Nth match for a selector (e.g. grid inputs)."""
        ctx = f"{truncate_for_log(selector)}[{index}]"

        def _build() -> Locator:
            return self._page.locator(selector).nth(index)

        return self._run("locator_nth", ctx, _build)
