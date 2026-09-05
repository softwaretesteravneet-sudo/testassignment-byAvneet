from __future__ import annotations

from playwright.sync_api import Locator, Page

from config.browser import BrowserSettings, get_browser_settings
from config.settings import Settings
from utils.logger import get_logger


class BasePage:
    def __init__(
        self,
        page: Page,
        settings: Settings,
        browser_settings: BrowserSettings | None = None,
    ) -> None:
        self.page = page
        self.settings = settings
        self.browser_settings = browser_settings or get_browser_settings()
        self.log = get_logger(self.__class__.__name__)

    def goto(self, url: str) -> None:
        self.log.info("Open %s", url)
        self.page.goto(url, wait_until="domcontentloaded")

    def test_id(self, value: str) -> Locator:
        return self.page.get_by_test_id(value)

    def wait_for_vue_app(self, ready_test_id: str) -> None:
        self.log.debug("Wait for Vue control %s", ready_test_id)
        self.test_id(ready_test_id).wait_for(state="visible")
