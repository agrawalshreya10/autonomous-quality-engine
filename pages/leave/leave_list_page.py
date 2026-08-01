"""Leave list page object for OrangeHRM."""

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
        return self.get_resilient_role_button("Search", 'button:has-text("Search")')

    @property
    def module_forbidden_heading(self) -> Locator:
        """Shared demo sometimes disables Leave → 403 Module Forbidden (no Search chrome)."""
        return self._page.get_by_role("heading", name="Module Forbidden")

    @property
    def results_table_body(self) -> Locator:
        return self._page.locator(".oxd-table-body").first

    def is_module_forbidden(self) -> bool:
        """True when the session cannot open Leave (demo ACL / module toggle)."""
        return self.is_visible(
            self.module_forbidden_heading,
            element_label="Module Forbidden heading",
        )

    def is_loaded(self) -> bool:
        """True if leave list chrome is ready (heading/table visibility varies)."""
        self.wait_for_url(LEAVE_LIST_URL, timeout_ms=self._settings.timeout_ms)
        if self.is_module_forbidden():
            raise PermissionError(
                "OrangeHRM Leave returned 403 Module Forbidden "
                "(shared demo ACL); Search button will not appear."
            )
        self.wait_for_visible(
            self.search_button,
            element_label="Leave list Search button",
            timeout_ms=self._settings.timeout_ms,
        )
        return True
