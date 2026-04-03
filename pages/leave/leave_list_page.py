"""Leave list page object for OrangeHRM."""

from playwright.sync_api import Locator, Page

from config.settings import Settings
from core.base_page import BasePage


class LeaveListPage(BasePage):
    """OrangeHRM Leave list: /web/index.php/leave/viewLeaveList."""

    def __init__(self, page: Page, settings: Settings) -> None:
        super().__init__(page, settings, path="web/index.php/leave/viewLeaveList")

    @property
    def leave_list_heading(self) -> Locator:
        return self._page.locator("h6").filter(has_text="Leave List").first

    @property
    def table_or_empty(self) -> Locator:
        return self._page.locator(".oxd-table-body")

    def is_loaded(self) -> bool:
        """True if leave list page is visible."""
        self.wait_for_url("**/leave/viewLeaveList**", timeout_ms=self._settings.timeout_ms)
        return self.is_visible(self.leave_list_heading, element_label="Leave List heading")
