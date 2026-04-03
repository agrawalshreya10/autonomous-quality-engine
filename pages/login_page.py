"""Login page object for OrangeHRM."""

from playwright.sync_api import Locator, Page

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
        return self._page.locator(".oxd-alert-content-text")

    def login(self, username: str, password: str) -> DashboardPage:
        """Enter credentials, click Login, return Dashboard page object."""
        self.navigate()
        self.fill(self.username_input, username, element_label="Username field")
        self.fill(self.password_input, password, element_label="Password field")
        self.click(self.login_button, element_label="Login button")
        return DashboardPage(self._page, self._settings)

    def get_error_text(self) -> str:
        """Return visible error message text if present."""
        if self.is_visible(self.error_message, element_label="Login error alert"):
            return self.get_text(self.error_message, element_label="Login error alert")
        return ""

    def is_login_page_visible(self) -> bool:
        """True if username field and login button are visible."""
        return self.is_visible(self.username_input, element_label="Username field") and self.is_visible(
            self.login_button,
            element_label="Login button",
        )
