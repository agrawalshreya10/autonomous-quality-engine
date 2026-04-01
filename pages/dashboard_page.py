"""Dashboard page object for OrangeHRM (post-login)."""

from playwright.sync_api import Page

from config.settings import Settings
from core.base_page import BasePage


class DashboardPage(BasePage):
    """OrangeHRM dashboard: /web/index.php/dashboardIndex."""

    def __init__(self, page: Page, settings: Settings) -> None:
        super().__init__(page, settings, path="web/index.php/dashboardIndex")

    @property
    def dashboard_heading(self):
        return self._page.get_by_role("heading", name="Dashboard")

    @property
    def user_dropdown(self):
        return self._page.locator(".oxd-userdropdown-tab")

    @property
    def logout_link(self):
        return self._page.get_by_role("menuitem", name="Logout")

    def is_loaded(self) -> bool:
        """True if dashboard is visible (user is logged in)."""
        self._page.wait_for_url("**/dashboardIndex**", timeout=self._settings.timeout_ms)
        return self.dashboard_heading.is_visible()

    def logout(self) -> None:
        """Click user dropdown and Logout."""
        self.user_dropdown.click()
        self.logout_link.click()
