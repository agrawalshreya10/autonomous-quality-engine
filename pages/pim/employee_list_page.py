"""PIM Employee List page object."""

from playwright.sync_api import Page

from config.settings import Settings
from core.base_page import BasePage


class EmployeeListPage(BasePage):
    """OrangeHRM PIM Employee List: /web/index.php/pim/viewEmployeeList."""

    def __init__(self, page: Page, settings: Settings) -> None:
        super().__init__(page, settings, path="web/index.php/pim/viewEmployeeList")

    @property
    def employee_table(self):
        return self._page.locator(".oxd-table-body")

    @property
    def no_records_message(self):
        return self._page.get_by_text("No Records Found")

    @property
    def search_employee_name_input(self):
        return self._page.get_by_placeholder("Type for hints...").first

    @property
    def search_button(self):
        return self._page.get_by_role("button", name="Search")

    @property
    def add_button(self):
        return self._page.get_by_role("button", name="Add")

    def navigate_to_list(self) -> "EmployeeListPage":
        """Navigate to employee list and return self."""
        self.navigate()
        return self

    def is_loaded(self) -> bool:
        """True if table or 'No Records' is visible."""
        self._page.wait_for_url("**/pim/viewEmployeeList**", timeout=self._settings.timeout_ms)
        return self.employee_table.is_visible() or self.no_records_message.is_visible()

    def search_by_employee_name(self, name: str) -> "EmployeeListPage":
        """Type in employee name search and click Search."""
        self.search_employee_name_input.fill(name)
        self.search_button.click()
        self._page.wait_for_load_state("networkidle")
        return self

    def get_row_count(self) -> int:
        """Number of data rows in the table."""
        return self._page.locator(".oxd-table-card").count()

    def click_add(self) -> "AddEmployeePage":
        """Click Add and return Add Employee page."""
        from pages.pim.add_employee_page import AddEmployeePage

        self.add_button.click()
        return AddEmployeePage(self._page, self._settings)
