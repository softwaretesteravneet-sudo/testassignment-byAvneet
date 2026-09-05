import pytest

from pages.dashboard_page import DashboardPage
from pages.login_page import LoginPage
from testdata.users import standard_user


@pytest.mark.smoke
@pytest.mark.login
def test_standard_login_positive_flow(
    login_page: LoginPage,
    dashboard_page: DashboardPage,
) -> None:
    login_page.open().expect_ready()
    login_page.login(standard_user())
    dashboard_page.wait_until_loaded().expect_authenticated()
