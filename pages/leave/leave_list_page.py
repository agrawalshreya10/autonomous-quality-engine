"""Leave list page object for OrangeHRM."""

import re

from playwright.sync_api import Locator, Page

from config.settings import Settings
from core.base_page import BasePage
from core.orangehrm_urls import LEAVE_LIST_URL


class LeaveListPage(BasePage):
    """OrangeHRM Leave list: /web/index.php/leave/viewLeaveList."""

    def __init__(self, page: Page, settings: Settings) -> None:
        super().__init__(page, settings, path="web/index.php/leave/viewLeaveList")

    @property
    def search_button(self) -> Locator:
        """Toolbar action; table .oxd-table-body can stay hidden until data loads on some builds."""
        return self._page.get_by_role("button", name=re.compile(r"^search$", re.IGNORECASE)).first

    @property
    def results_table_body(self) -> Locator:
        return self._page.locator(".oxd-table-body").first

    def is_loaded(self) -> bool:
        """True if leave list chrome is ready (heading/table visibility varies)."""
        self.wait_for_url(LEAVE_LIST_URL, timeout_ms=self._settings.timeout_ms)
        self.wait_for_visible(
            self.search_button,
            element_label="Leave list Search button",
            timeout_ms=self._settings.timeout_ms,
        )
        return True
