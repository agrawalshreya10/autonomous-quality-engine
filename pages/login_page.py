"""Login page object for OrangeHRM."""

import json
import time

from playwright.sync_api import Locator, Page, expect

from config.settings import Settings
from core.base_page import BasePage
from pages.dashboard_page import DashboardPage


class LoginPage(BasePage):
    """OrangeHRM login page: /web/index.php/auth/login."""

    def __init__(self, page: Page, settings: Settings) -> None:
        super().__init__(page, settings, path="web/index.php/auth/login")

    # Locators (OrangeHRM 5.x + legacy ids for self-healing on local / ohrm.test)
    @property
    def username_input(self) -> Locator:
        return self.get_resilient_locator('input[name="username"]', "#txtUsername")

    @property
    def password_input(self) -> Locator:
        return self.get_resilient_locator('input[name="password"]', "#txtPassword")

    @property
    def login_button(self) -> Locator:
        return self.get_resilient_locator('button[type="submit"]', "#btnLogin")

    @property
    def error_message(self) -> Locator:
        # Union: Oxd alert text span, or ARIA alert (demo / skin variants).
        return self._page.locator(".oxd-alert-content-text").or_(
            self._page.get_by_role("alert")
        )

    def login(self, username: str, password: str) -> DashboardPage:
        """Enter credentials, click Login, return Dashboard page object."""
        self.navigate()
        self.fill(self.username_input, username, element_label="Username field")
        self.fill(self.password_input, password, element_label="Password field")
        self.click(self.login_button, element_label="Login button")
        return DashboardPage(self._page, self._settings)

    def get_error_text(self) -> str:
        """Return visible error message text if present (waits for alert; see debug log)."""
        # region agent log
        _log_path = "/Users/ShreyaAgrawal/Work/autonomous-quality-engine/.cursor/debug-67321a.log"

        def _dbg(msg: str, data: dict, hid: str) -> None:
            try:
                line = {
                    "sessionId": "67321a",
                    "timestamp": int(time.time() * 1000),
                    "location": "login_page.py:get_error_text",
                    "message": msg,
                    "data": data,
                    "hypothesisId": hid,
                }
                with open(_log_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(line, ensure_ascii=False) + "\n")
            except OSError:
                pass

        # endregion
        # is_visible() does not wait; the alert often appears after navigation/inputs settle.
        try:
            expect(self.error_message).to_be_visible(timeout=self._settings.timeout_ms)
        except Exception as e:
            _dbg(
                "login_error_not_visible",
                {"exc_type": type(e).__name__},
                "H1",
            )
            return ""
        text = self.get_text(self.error_message, element_label="Login error alert")
        _dbg("login_error_text_ok", {"text_len": len(text)}, "H1")
        return text

    def is_login_page_visible(self) -> bool:
        """True if username field and login button are visible."""
        return self.is_visible(self.username_input, element_label="Username field") and self.is_visible(
            self.login_button,
            element_label="Login button",
        )
