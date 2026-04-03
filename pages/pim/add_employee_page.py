"""PIM Add Employee page object."""

from playwright.sync_api import Locator, Page

from config.settings import Settings
from core.base_page import BasePage


class AddEmployeePage(BasePage):
    """OrangeHRM PIM Add Employee: /web/index.php/pim/addEmployee."""

    def __init__(self, page: Page, settings: Settings) -> None:
        super().__init__(page, settings, path="web/index.php/pim/addEmployee")

    @property
    def first_name_input(self) -> Locator:
        return self.get_resilient_locator('input[name="firstName"]', "#firstName")

    @property
    def last_name_input(self) -> Locator:
        return self.get_resilient_locator('input[name="lastName"]', "#lastName")

    @property
    def employee_id_input(self) -> Locator:
        return self.locator_nth(".oxd-grid-2 input", 2, element_label="Employee ID input")

    @property
    def save_button(self) -> Locator:
        return self.get_resilient_role_button("Save", 'button[type="submit"]:has-text("Save")')

    @property
    def success_toast(self) -> Locator:
        return self._page.locator(".oxd-toast-content")

    @property
    def validation_error(self) -> Locator:
        return self._page.locator(".oxd-input-field-error-message")

    def is_loaded(self) -> bool:
        """True if add employee form is visible."""
        self.wait_for_url("**/pim/addEmployee**", timeout_ms=self._settings.timeout_ms)
        return self.is_visible(self.first_name_input, element_label="Employee first name field")

    def fill_employee(
        self,
        first_name: str,
        last_name: str,
        employee_id: str = "",
    ) -> "AddEmployeePage":
        """Fill first name, last name, and optional employee id."""
        self.fill(self.first_name_input, first_name, element_label="Employee first name")
        self.fill(self.last_name_input, last_name, element_label="Employee last name")
        if employee_id:
            self.fill(self.employee_id_input, employee_id, element_label="Employee ID")
        return self

    def save(self) -> "EmployeeListPage":
        """Click Save and return Employee List page."""
        from pages.pim.employee_list_page import EmployeeListPage

        self.click(self.save_button, element_label="Save employee button")
        return EmployeeListPage(self._page, self._settings)

    def save_expect_success(self) -> "EmployeeListPage":
        """Save and wait for success toast, then return list page."""
        from pages.pim.employee_list_page import EmployeeListPage

        self.click(self.save_button, element_label="Save employee button")
        self.wait_for_visible(self.success_toast, element_label="Success toast")
        return EmployeeListPage(self._page, self._settings)

    def get_validation_errors(self) -> list[str]:
        """Return list of visible validation error messages."""

        def _collect() -> list[str]:
            return [el.inner_text() for el in self.validation_error.all() if el.is_visible()]

        return self._run("get_validation_errors", "PIM validation messages", _collect)
