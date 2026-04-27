"""Login page object for OrangeHRM."""

from playwright.sync_api import Locator, Page, TimeoutError, expect

from config.settings import Settings
from core.base_page import BasePage
from pages.dashboard_page import DashboardPage


class LoginPage(BasePage):
    """OrangeHRM login page: /web/index.php/auth/login."""

    def __init__(self, page: Page, settings: Settings) -> None:
        super().__init__(page, settings, path="web/index.php/auth/login")

    # Locators (OrangeHRM 5.x + legacy ids for self-healing on local / ohrm.test)
    @property
    def username_input(self) -> Locator:
        return self.get_resilient_locator('input[name="username"]', "#txtUsername")

    @property
    def password_input(self) -> Locator:
        return self.get_resilient_locator('input[name="password"]', "#txtPassword")

    @property
    def login_button(self) -> Locator:
        return self.get_resilient_locator('button[type="submit"]', "#btnLogin")

    @property
    def error_message(self) -> Locator:
        # Single node: the visible message is `.oxd-alert-content-text` inside `role=alert`.
        # Do NOT union `locator(".oxd-alert-content-text").or_(get_by_role("alert"))` — that
        # resolves to two elements (parent div + child <p>), and expect() strict mode fails.
        return self._page.locator(".oxd-alert-content-text")

    def login(self, username: str, password: str) -> DashboardPage:
        """Enter credentials, click Login, return Dashboard page object."""
        try:
            self.navigate()
            self.fill(self.username_input, username, element_label="Username field")
            self.fill(self.password_input, password, element_label="Password field")
            self.click(self.login_button, element_label="Login button")
            return DashboardPage(self._page, self._settings)
        except Exception:
            self._error_logger.exception("login failed")
            raise

    def get_error_text(self) -> str:
        """Return visible login error text if present; waits for the alert (web-first)."""
        try:
            # is_visible() does not wait; the alert often appears after the failed login response.
            try:
                expect(self.error_message).to_be_visible(timeout=self._settings.timeout_ms)
            except TimeoutError:
                # No login error displayed (expected for successful login flows).
                return ""
            except Exception:
                # Unexpected Playwright/runtime error: log and re-raise (see `.cursor/rules/page-object-standards.mdc`).
                self._error_logger.exception("Failed to read login error alert text")
                raise
            return self.get_text(self.error_message, element_label="Login error alert")
        except Exception:
            self._error_logger.exception("get_error_text failed")
            raise

    def is_login_page_visible(self) -> bool:
        """True if username field and login button are visible."""
        try:
            return self.is_visible(self.username_input, element_label="Username field") and self.is_visible(
                self.login_button,
                element_label="Login button",
            )
        except Exception:
            self._error_logger.exception("is_login_page_visible failed")
            raise
