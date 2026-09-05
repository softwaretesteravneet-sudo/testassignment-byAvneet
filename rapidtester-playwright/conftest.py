from __future__ import annotations

from pathlib import Path

import pytest
from playwright.sync_api import Page

from config.browser import BrowserSettings, get_browser_settings
from config.settings import Settings, get_settings
from pages.auth0_page import Auth0Page
from pages.dashboard_page import DashboardPage
from pages.login_page import LoginPage
from pages.registration_page import RegistrationPage
from utils.chrome import ensure_google_chrome
from utils.logger import configure_logging, get_logger
from utils.reporting import apply_report_paths, new_execution_dir

log = get_logger("pytest")


def _label_tests_as_chrome(items: list[pytest.Item]) -> None:
    """Playwright's engine id is 'chromium'; this suite launches Google Chrome."""
    for item in items:
        if "[chromium]" in item.nodeid:
            item._nodeid = item.nodeid.replace("[chromium]", "[chrome]")


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config: pytest.Config) -> None:
    workerinput = getattr(config, "workerinput", None)
    if workerinput and workerinput.get("execution_report_dir"):
        execution_dir = Path(workerinput["execution_report_dir"])
    else:
        execution_dir = new_execution_dir()
    apply_report_paths(config, execution_dir)
    configure_logging(execution_dir)
    if not workerinput:
        ensure_google_chrome()


def pytest_sessionstart(session: pytest.Session) -> None:
    try:
        from pytest_metadata.plugin import metadata_key

        session.config.stash[metadata_key]["Browser"] = "Google Chrome"
    except (ImportError, KeyError):
        pass


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    _label_tests_as_chrome(items)


def pytest_configure_node(node) -> None:
    node.workerinput["execution_report_dir"] = node.config.execution_report_dir


def pytest_runtest_setup(item: pytest.Item) -> None:
    log.info("START %s", item.nodeid)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo) -> None:
    outcome = yield
    report = outcome.get_result()
    if report.when != "call":
        return

    page = item.funcargs.get("page") if hasattr(item, "funcargs") else None
    url = f" | url={page.url}" if page else ""

    if report.passed:
        log.info("PASSED %s%s", item.nodeid, url)
        return
    if report.skipped:
        reason = ""
        if report.longrepr:
            reason = str(report.longrepr[-1] if isinstance(report.longrepr, tuple) else report.longrepr)
        log.warning("SKIPPED %s | %s", item.nodeid, reason)
        return
    if report.failed:
        log.error("FAILED %s%s", item.nodeid, url)
        if report.longrepr:
            log.error("%s", report.longrepr)


def pytest_terminal_summary(terminalreporter, config: pytest.Config) -> None:
    report_dir = getattr(config, "execution_report_dir", None)
    if report_dir:
        terminalreporter.write_sep("-", f"Execution reports: {report_dir}")
        log_path = getattr(config, "suite_log_path", None)
        if log_path:
            terminalreporter.write_line(f"Suite log: {log_path}")


@pytest.fixture(scope="session")
def settings() -> Settings:
    return get_settings()


@pytest.fixture(scope="session")
def browser_settings() -> BrowserSettings:
    return get_browser_settings()


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args: dict, browser_settings: BrowserSettings) -> dict:
    return {**browser_type_launch_args, **browser_settings.launch_options()}


@pytest.fixture(scope="session")
def browser_context_args(
    browser_context_args: dict,
    settings: Settings,
    browser_settings: BrowserSettings,
) -> dict:
    return {
        **browser_context_args,
        **browser_settings.context_options(
            settings.base_url,
            settings.basic_auth_username,
            settings.basic_auth_password,
        ),
    }


@pytest.fixture
def page(page: Page, browser_settings: BrowserSettings) -> Page:
    page.set_default_timeout(browser_settings.default_timeout_ms)
    page.set_default_navigation_timeout(browser_settings.navigation_timeout_ms)
    return page


@pytest.fixture
def login_page(page: Page, settings: Settings) -> LoginPage:
    return LoginPage(page, settings)


@pytest.fixture
def registration_page(page: Page, settings: Settings) -> RegistrationPage:
    return RegistrationPage(page, settings)


@pytest.fixture
def auth0_page(page: Page, settings: Settings) -> Auth0Page:
    return Auth0Page(page, settings)


@pytest.fixture
def dashboard_page(page: Page, settings: Settings) -> DashboardPage:
    return DashboardPage(page, settings)
