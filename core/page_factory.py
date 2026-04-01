"""Factory for creating page objects with shared driver and config."""

from typing import Type, TypeVar

from playwright.sync_api import Page

from config.settings import Settings
from core.base_page import BasePage

T = TypeVar("T", bound=BasePage)


class PageFactory:
    """Creates and caches page objects for the current Playwright page."""

    def __init__(self, page: Page, settings: Settings) -> None:
        self._page = page
        self._settings = settings
        self._cache: dict[type[BasePage], BasePage] = {}

    def get_page(self, page_class: Type[T]) -> T:
        """Return a (cached) instance of the requested page class."""
        if page_class not in self._cache:
            self._cache[page_class] = page_class(self._page, self._settings)
        return self._cache[page_class]  # type: ignore[return-value]

    @property
    def page(self) -> Page:
        return self._page

    @property
    def settings(self) -> Settings:
        return self._settings
