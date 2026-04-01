"""PIM Add Employee page object."""

from playwright.sync_api import Page

from config.settings import Settings
from core.base_page import BasePage


class AddEmployeePage(BasePage):
    """OrangeHRM PIM Add Employee: /web/index.php/pim/addEmployee."""

    def __init__(self, page: Page, settings: Settings) -> None:
        super().__init__(page, settings, path="web/index.php/pim/addEmployee")

    @property
    def first_name_input(self):
        return self._page.locator('input[name="firstName"]')

    @property
    def last_name_input(self):
        return self._page.locator('input[name="lastName"]')

    @property
    def employee_id_input(self):
        return self._page.locator(".oxd-grid-2 input").nth(2)  # Employee Id in form

    @property
    def save_button(self):
        return self._page.get_by_role("button", name="Save")

    @property
    def success_toast(self):
        return self._page.locator(".oxd-toast-content")

    @property
    def validation_error(self):
        return self._page.locator(".oxd-input-field-error-message")

    def is_loaded(self) -> bool:
        """True if add employee form is visible."""
        self._page.wait_for_url("**/pim/addEmployee**", timeout=self._settings.timeout_ms)
        return self.first_name_input.is_visible()

    def fill_employee(
        self,
        first_name: str,
        last_name: str,
        employee_id: str = "",
    ) -> "AddEmployeePage":
        """Fill first name, last name, and optional employee id."""
        self.first_name_input.fill(first_name)
        self.last_name_input.fill(last_name)
        if employee_id:
            self.employee_id_input.fill(employee_id)
        return self

    def save(self) -> "EmployeeListPage":
        """Click Save and return Employee List page."""
        from pages.pim.employee_list_page import EmployeeListPage

        self.save_button.click()
        return EmployeeListPage(self._page, self._settings)

    def save_expect_success(self) -> "EmployeeListPage":
        """Save and wait for success toast, then return list page."""
        from pages.pim.employee_list_page import EmployeeListPage

        self.save_button.click()
        self.success_toast.wait_for(state="visible", timeout=self._settings.timeout_ms)
        return EmployeeListPage(self._page, self._settings)

    def get_validation_errors(self) -> list[str]:
        """Return list of visible validation error messages."""
        return [el.inner_text() for el in self.validation_error.all() if el.is_visible()]
