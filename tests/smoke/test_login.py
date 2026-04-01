"""Smoke tests: login success, invalid credentials, logout.

Uses BASE_URL and credentials from config (`.env` / environment) so local
instances (MAMP, custom port, HTTPS) match Playwright context and login steps.
"""

import pytest

from pages.dashboard_page import DashboardPage
from pages.login_page import LoginPage


@pytest.mark.smoke
def test_login_success(page_factory):
    """Valid credentials should land on dashboard."""
    settings = page_factory.settings
    login_page = page_factory.get_page(LoginPage)
    login_page.navigate()
    dashboard = login_page.login(settings.orangehrm_user, settings.orangehrm_password)
    assert dashboard.is_loaded()


@pytest.mark.smoke
def test_login_invalid_credentials(page_factory):
    """Invalid password should show error and stay on login page."""
    settings = page_factory.settings
    login_page = page_factory.get_page(LoginPage)
    login_page.navigate()
    login_page.login(settings.orangehrm_user, "wrongpassword")
    assert login_page.is_login_page_visible()
    error = login_page.get_error_text()
    assert "Invalid credentials" in error or "Invalid" in error or len(error) > 0


@pytest.mark.smoke
def test_login_then_logout(page_factory):
    """Login then logout should return to login page."""
    settings = page_factory.settings
    login_page = page_factory.get_page(LoginPage)
    login_page.navigate()
    dashboard = login_page.login(settings.orangehrm_user, settings.orangehrm_password)
    assert dashboard.is_loaded()
    dashboard.logout()
    login_page._page.wait_for_url("**/auth/login**", timeout=settings.timeout_ms)
    assert login_page.is_login_page_visible()
