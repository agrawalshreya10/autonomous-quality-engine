"""URL patterns for OrangeHRM 5.x routes (hosted demo + local).

OrangeHRM 5.8+ often uses /dashboard/index; older builds used dashboardIndex in the path.
Use these with BasePage.wait_for_url (regex) for resilient assertions across environments.
"""

import re

# Post-login dashboard: .../dashboard/index or .../dashboardIndex
DASHBOARD_URL = re.compile(
    r".*(/dashboard/(index|dashboardIndex)|/dashboardIndex)(/|\?|$|#).*",
    re.IGNORECASE,
)

# Route segments vary by build; match stable action names in the path/query.
PIM_EMPLOYEE_LIST_URL = re.compile(r".*viewEmployeeList.*", re.IGNORECASE)
PIM_ADD_EMPLOYEE_URL = re.compile(r".*addEmployee.*", re.IGNORECASE)
LEAVE_LIST_URL = re.compile(r".*viewLeaveList.*", re.IGNORECASE)
