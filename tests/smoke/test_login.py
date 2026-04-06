"""Smoke tests: login success, invalid credentials, logout.

Uses BASE_URL and credentials from config (`.env` / environment) so local
instances (MAMP, custom port, HTTPS) match Playwright context and login steps.
"""

import pytest
from playwright.sync_api import expect

from pages.login_page import LoginPage


@pytest.mark.smoke
def test_login_success(page_factory):
    """Valid credentials should land on dashboard."""
    settings = page_factory.settings
    login_page = page_factory.get_page(LoginPage)
    login_page.navigate()
    # TEMPORARY: Using wrong password to test CI failure analyzer - REVERT THIS LATER
    dashboard = login_page.login(settings.orangehrm_user, "WRONG_PASSWORD_FOR_CI_TEST")
    assert dashboard.is_loaded()


@pytest.mark.smoke
def test_login_invalid_credentials(page_factory):
    """Invalid password should show error and stay on login page."""
    settings = page_factory.settings
    login_page = page_factory.get_page(LoginPage)
    login_page.navigate()
    login_page.login(settings.orangehrm_user, "wrongpassword")
    login_page.wait_for_url("**/auth/login**", timeout_ms=settings.timeout_ms)
    expect(login_page.username_input).to_be_visible(timeout=settings.timeout_ms)
    expect(login_page.password_input).to_be_visible(timeout=settings.timeout_ms)
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
    login_page.wait_for_url("**/auth/login**", timeout_ms=settings.timeout_ms)
    expect(login_page.username_input).to_be_visible(timeout=settings.timeout_ms)
    expect(login_page.login_button).to_be_visible(timeout=settings.timeout_ms)
