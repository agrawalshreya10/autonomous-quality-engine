"""Playwright browser and context lifecycle management."""

from typing import TYPE_CHECKING

from playwright.sync_api import Browser, BrowserContext, Page, sync_playwright

from config.settings import Settings, get_settings

if TYPE_CHECKING:
    pass


def create_browser_context(
    settings: Settings | None = None,
    **context_options: object,
) -> tuple[sync_playwright, Browser, BrowserContext]:
    """
    Start Playwright, launch browser, create a new context.
    Returns (playwright, browser, context). Caller must call playwright.stop() when done.
    """
    settings = settings or get_settings()
    playwright = sync_playwright().start()
    launch_opts = {"headless": settings.headless, "slow_mo": settings.slow_mo_ms}
    if settings.browser == "firefox":
        browser = playwright.firefox.launch(**launch_opts)
    elif settings.browser == "webkit":
        browser = playwright.webkit.launch(**launch_opts)
    else:
        browser = playwright.chromium.launch(**launch_opts)
    context = browser.new_context(
        base_url=settings.base_url,
        viewport={"width": 1920, "height": 1080},
        ignore_https_errors=settings.ignore_https_errors,
        **context_options,
    )
    context.set_default_timeout(settings.timeout_ms)
    return playwright, browser, context


def create_page(
    settings: Settings | None = None,
    **context_options: object,
) -> tuple[sync_playwright, Browser, BrowserContext, Page]:
    """
    Create a new page in a fresh context. Returns (playwright, browser, context, page).
    Caller must call playwright.stop() when done.
    """
    playwright, browser, context = create_browser_context(
        settings=settings, **context_options
    )
    page = context.new_page()
    return playwright, browser, context, page
