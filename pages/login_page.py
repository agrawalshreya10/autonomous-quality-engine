"""Login page object for OrangeHRM."""

from playwright.sync_api import Page

from config.settings import Settings
from core.base_page import BasePage
from pages.dashboard_page import DashboardPage


class LoginPage(BasePage):
    """OrangeHRM login page: /web/index.php/auth/login."""

    def __init__(self, page: Page, settings: Settings) -> None:
        super().__init__(page, settings, path="web/index.php/auth/login")

    # Locators (OrangeHRM 5.x)
    @property
    def username_input(self):
        return self._page.locator('input[name="username"]')

    @property
    def password_input(self):
        return self._page.locator('input[name="password"]')

    @property
    def login_button(self):
        return self._page.locator('button[type="submit"]')

    @property
    def error_message(self):
        return self._page.locator(".oxd-alert-content-text")

    def login(self, username: str, password: str) -> DashboardPage:
        """Enter credentials, click Login, return Dashboard page object."""
        self.navigate()
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.login_button.click()
        return DashboardPage(self._page, self._settings)

    def get_error_text(self) -> str:
        """Return visible error message text if present."""
        if self.error_message.is_visible():
            return self.error_message.inner_text()
        return ""

    def is_login_page_visible(self) -> bool:
        """True if username field and login button are visible."""
        return self.username_input.is_visible() and self.login_button.is_visible()
