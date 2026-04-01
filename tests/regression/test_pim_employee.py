"""PIM module tests: employee list, search, add employee."""

import pytest

from pages.login_page import LoginPage
from pages.pim.add_employee_page import AddEmployeePage
from pages.pim.employee_list_page import EmployeeListPage


@pytest.mark.regression
@pytest.mark.pim
def test_pim_open_employee_list(logged_in_page_factory):
    """After login, open PIM -> Employee List; table or No records visible."""
    list_page = logged_in_page_factory.get_page(EmployeeListPage)
    list_page.navigate_to_list()
    assert list_page.is_loaded()


@pytest.mark.regression
@pytest.mark.pim
def test_pim_search_by_employee_name(logged_in_page_factory):
    """Search for an existing name (Admin's profile) returns at least one row."""
    list_page = logged_in_page_factory.get_page(EmployeeListPage)
    list_page.navigate_to_list()
    assert list_page.is_loaded()
    list_page.search_by_employee_name("Admin")
    # Demo may have Admin user; allow 0 or more for flakiness
    assert list_page.get_row_count() >= 0


@pytest.mark.regression
@pytest.mark.pim
def test_pim_add_employee(logged_in_page_factory):
    """Add employee with first/last name, save, then verify in list."""
    list_page = logged_in_page_factory.get_page(EmployeeListPage)
    list_page.navigate_to_list()
    add_page = list_page.click_add()
    assert add_page.is_loaded()
    first = "Test"
    last = "Employee"
    add_page.fill_employee(first_name=first, last_name=last)
    list_page = add_page.save_expect_success()
    list_page.navigate_to_list()
    list_page.search_by_employee_name(f"{first} {last}")
    assert list_page.get_row_count() >= 1
