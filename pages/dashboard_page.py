"""Dashboard page object for OrangeHRM (post-login)."""

from playwright.sync_api import Locator, Page

from config.settings import Settings
from core.base_page import BasePage
from core.orangehrm_urls import DASHBOARD_URL


class DashboardPage(BasePage):
    """OrangeHRM dashboard (5.8+: /dashboard/index; legacy: dashboardIndex)."""

    def __init__(self, page: Page, settings: Settings) -> None:
        super().__init__(page, settings, path="web/index.php/dashboard/index")

    @property
    def dashboard_heading(self) -> Locator:
        return self._page.get_by_role("heading", name="Dashboard")

    @property
    def user_dropdown(self) -> Locator:
        # Single match for strict wait_for/click; .or_(tab|name) unions two visible nodes.
        return self._page.locator(".oxd-userdropdown-tab").first

    @property
    def logout_link(self) -> Locator:
        return self.get_resilient_role_menuitem("Logout", 'a[role="menuitem"]:has-text("Logout")')

    def is_loaded(self) -> bool:
        """True if dashboard is visible (user is logged in)."""
        self.wait_for_url(DASHBOARD_URL, timeout_ms=self._settings.timeout_ms)
        # Heading text/lvl can differ by locale/build; user menu is a stable logged-in signal.
        self.wait_for_visible(self.user_dropdown, element_label="User account dropdown", timeout_ms=self._settings.timeout_ms)
        return True

    def logout(self) -> None:
        """Click user dropdown and Logout."""
        self.click(self.user_dropdown, element_label="User account dropdown")
        self.click(self.logout_link, element_label="Logout menu item")
