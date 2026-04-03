"""Dashboard page object for OrangeHRM (post-login)."""

from playwright.sync_api import Locator, Page

from config.settings import Settings
from core.base_page import BasePage


class DashboardPage(BasePage):
    """OrangeHRM dashboard: /web/index.php/dashboardIndex."""

    def __init__(self, page: Page, settings: Settings) -> None:
        super().__init__(page, settings, path="web/index.php/dashboardIndex")

    @property
    def dashboard_heading(self) -> Locator:
        return self._page.get_by_role("heading", name="Dashboard")

    @property
    def user_dropdown(self) -> Locator:
        return self.get_resilient_locator(".oxd-userdropdown-tab", "[class*='userdropdown']")

    @property
    def logout_link(self) -> Locator:
        return self.get_resilient_role_menuitem("Logout", 'a[role="menuitem"]:has-text("Logout")')

    def is_loaded(self) -> bool:
        """True if dashboard is visible (user is logged in)."""
        self.wait_for_url("**/dashboardIndex**", timeout_ms=self._settings.timeout_ms)
        return self.is_visible(self.dashboard_heading, element_label="Dashboard heading")

    def logout(self) -> None:
        """Click user dropdown and Logout."""
        self.click(self.user_dropdown, element_label="User account dropdown")
        self.click(self.logout_link, element_label="Logout menu item")
