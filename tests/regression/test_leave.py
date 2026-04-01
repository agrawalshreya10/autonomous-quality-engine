"""Leave module tests: open leave list, navigation."""

import pytest

from pages.dashboard_page import DashboardPage
from pages.leave.leave_list_page import LeaveListPage
from pages.pim.employee_list_page import EmployeeListPage


@pytest.mark.regression
@pytest.mark.leave
def test_leave_open_leave_list(logged_in_page_factory):
    """Navigate to Leave -> Leave list; page loads."""
    leave_page = logged_in_page_factory.get_page(LeaveListPage)
    leave_page.navigate()
    assert leave_page.is_loaded()


@pytest.mark.regression
@pytest.mark.leave
def test_navigation_pim_and_leave(logged_in_page_factory):
    """After login, open PIM then Leave and assert correct headings."""
    list_page = logged_in_page_factory.get_page(EmployeeListPage)
    list_page.navigate_to_list()
    assert list_page.is_loaded()

    leave_page = logged_in_page_factory.get_page(LeaveListPage)
    leave_page.navigate()
    assert leave_page.is_loaded()
