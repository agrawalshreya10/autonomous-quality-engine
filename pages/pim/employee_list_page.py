"""PIM Employee List page object."""

from playwright.sync_api import Locator, Page

from config.settings import Settings
from core.base_page import BasePage
from core.orangehrm_urls import PIM_EMPLOYEE_LIST_URL


class EmployeeListPage(BasePage):
    """OrangeHRM PIM Employee List: /web/index.php/pim/viewEmployeeList."""

    def __init__(self, page: Page, settings: Settings) -> None:
        super().__init__(page, settings, path="web/index.php/pim/viewEmployeeList")

    @property
    def employee_table(self) -> Locator:
        return self._page.locator(".oxd-table-body")

    @property
    def no_records_message(self) -> Locator:
        return self._page.get_by_text("No Records Found")

    @property
    def search_employee_name_input(self) -> Locator:
        return self.get_resilient_placeholder("Type for hints...", "Employee Name")

    @property
    def search_button(self) -> Locator:
        return self.get_resilient_role_button("Search", 'button:has-text("Search")')

    @property
    def add_button(self) -> Locator:
        return self.get_resilient_role_button("Add", 'button:has-text("Add")')

    def navigate_to_list(self) -> "EmployeeListPage":
        """Navigate to employee list and return self."""
        self.navigate()
        return self

    def is_loaded(self) -> bool:
        """True if table or 'No Records' is visible."""
        self.wait_for_url(PIM_EMPLOYEE_LIST_URL, timeout_ms=self._settings.timeout_ms)
        content = self.employee_table.or_(self.no_records_message)
        self.wait_for_visible(content, element_label="Employee list table or empty state", timeout_ms=self._settings.timeout_ms)
        return True

    def search_by_employee_name(self, name: str) -> "EmployeeListPage":
        """Type in employee name search and click Search."""
        self.fill(self.search_employee_name_input, name, element_label="Employee name search field")
        self.click(self.search_button, element_label="Search employees button")
        self.wait_for_load_state("networkidle")
        return self

    def get_row_count(self) -> int:
        """Number of data rows in the table."""
        return self.count_locator_matches(".oxd-table-card", element_label="Employee table data rows")

    def click_add(self) -> "AddEmployeePage":
        """Click Add and return Add Employee page."""
        from pages.pim.add_employee_page import AddEmployeePage

        self.click(self.add_button, element_label="Add Employee button")
        return AddEmployeePage(self._page, self._settings)
