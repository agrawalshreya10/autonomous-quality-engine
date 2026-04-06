"""Pytest fixtures: driver lifecycle, page factory, and optional logged-in session."""

import os
import subprocess
import sys
from pathlib import Path

import pytest
from playwright.sync_api import expect

from config.settings import get_settings
from core.driver import create_browser_context
from core.orangehrm_urls import DASHBOARD_URL
from core.page_factory import PageFactory


def pytest_configure(config):
    """Ensure reports dir exists; reset failures.txt for AI audit."""
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    (reports_dir / "screenshots").mkdir(exist_ok=True)
    failures_file = reports_dir / "failures.txt"
    if failures_file.exists():
        failures_file.write_text("")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Capture screenshot on test failure when page fixture is available."""
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        if "page" in item.fixturenames:
            page = item.funcargs.get("page", None)
            if page is not None:
                try:
                    path = Path("reports/screenshots") / f"{item.name}.png"
                    path.parent.mkdir(parents=True, exist_ok=True)
                    page.screenshot(path=path)
                    report.screenshot_path = str(path)
                except Exception:
                    pass
        # Append to failures.txt for AI audit (python -m ai_audit.failure_analyzer)
        try:
            failures_file = Path("reports/failures.txt")
            failures_file.parent.mkdir(parents=True, exist_ok=True)
            msg = str(report.longrepr) if report.longrepr else report.nodeid
            with open(failures_file, "a") as f:
                f.write(f"TEST: {item.nodeid}\nMESSAGE: {msg}\n\n")
        except Exception:
            pass


def pytest_sessionfinish(session, exitstatus):
    """Auto-run AI failure analysis locally when tests fail."""
    # Only run locally (not in CI) and only on test failures
    if exitstatus != 0 and not os.environ.get("GITHUB_ACTIONS"):
        failures_file = Path("reports/failures.txt")
        if failures_file.exists() and failures_file.stat().st_size > 0:
            out_path = Path("reports/ai_suggestions.md")
            try:
                print("\n[AI-AUDIT] Test session failed. Starting automatic failure analysis...")
                subprocess.run(
                    [
                        sys.executable,
                        "-m",
                        "ai_audit.failure_analyzer",
                        "--client",
                        "auto",
                        "--artifacts-dir",
                        "reports",
                        "--out",
                        str(out_path),
                    ],
                    check=False,
                    timeout=120,
                )
                if out_path.is_file() and out_path.stat().st_size > 0:
                    print(f"[AI-AUDIT] Suggestions written to {out_path}")
            except subprocess.TimeoutExpired:
                print("[AI-AUDIT] Analysis timed out after 2 minutes.")
            except Exception as e:
                print(f"[AI-AUDIT] Analysis failed: {e}")


@pytest.fixture(scope="function")
def browser_context():
    """Create a new browser context and page per test. Yields (playwright, browser, context)."""
    settings = get_settings()
    playwright, browser, context = create_browser_context(settings=settings)
    yield playwright, browser, context
    playwright.stop()


@pytest.fixture(scope="function")
def page(browser_context):
    """New Playwright page per test (new context)."""
    playwright, browser, context = browser_context
    yield context.new_page()


@pytest.fixture(scope="function")
def page_factory(page):
    """PageFactory for the current test's page."""
    settings = get_settings()
    return PageFactory(page, settings)


@pytest.fixture(scope="function")
def logged_in_page_factory(page_factory):
    """PageFactory with user already logged in (navigates to login and logs in)."""
    from pages.login_page import LoginPage

    settings = get_settings()
    login_page = page_factory.get_page(LoginPage)
    login_page.login(settings.orangehrm_user, settings.orangehrm_password)
    # Avoid immediate deep-link goto while post-login redirect/navigation is still settling (ERR_ABORTED).
    expect(page_factory.page).to_have_url(DASHBOARD_URL, timeout=settings.timeout_ms)
    page_factory.page.wait_for_load_state("domcontentloaded")
    return page_factory
