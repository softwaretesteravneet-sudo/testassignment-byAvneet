from __future__ import annotations

from playwright.sync_api import expect

from pages.base_page import BasePage


class TwoFactorPage(BasePage):
    """Optional 2FA splash after a successful password login."""

    @property
    def skip_button(self):
        return self.test_id("two-factor-authentication-splash-screen-skip")

    @property
    def show_button(self):
        return self.test_id("two-factor-authentication-splash-screen-show")

    def is_open(self) -> bool:
        return "two-factor-authentication" in self.page.url

    def skip_if_present(self) -> None:
        if not self.is_open():
            return
        self.log.info("Skip optional 2FA splash")
        expect(self.skip_button).to_be_visible()
        self.skip_button.click()
