from __future__ import annotations

import re
from urllib.parse import urlparse

from playwright.sync_api import expect

from pages.base_page import BasePage
from pages.two_factor_page import TwoFactorPage


class DashboardPage(BasePage):
    def wait_until_loaded(self) -> "DashboardPage":
        app_host = re.escape(urlparse(self.settings.app_url).netloc)
        timeout = self.browser_settings.navigation_timeout_ms
        self.page.wait_for_url(
            re.compile(rf"(two-factor-authentication|/profiles|{app_host})"),
            timeout=timeout,
        )
        TwoFactorPage(self.page, self.settings).skip_if_present()
        self.page.wait_for_url(re.compile(rf"(/profiles|{app_host})"), timeout=timeout)
        self.log.info("Landed on %s", self.page.url)
        return self

    def expect_authenticated(self) -> None:
        app_host = re.escape(urlparse(self.settings.app_url).netloc)
        expect(self.page).to_have_url(re.compile(rf"(/profiles|{app_host})"))
        self.log.info("Authenticated session confirmed at %s", self.page.url)
