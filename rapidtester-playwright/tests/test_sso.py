import pytest

from pages.auth0_page import Auth0Page
from pages.dashboard_page import DashboardPage
from pages.login_page import LoginPage
from testdata.users import sso_user


@pytest.mark.smoke
@pytest.mark.sso
def test_sso_opens_auth0_with_valid_authorize_contract(
    login_page: LoginPage,
    auth0_page: Auth0Page,
) -> None:
    login_page.open().expect_ready()
    authorize = auth0_page.capture_authorize_url(login_page.start_sso)
    auth0_page.expect_authorize_contract(authorize)
    auth0_page.expect_provider_screen()


@pytest.mark.sso
def test_sso_completes_login_when_provider_accepts_identifier(
    login_page: LoginPage,
    auth0_page: Auth0Page,
    dashboard_page: DashboardPage,
) -> None:
    login_page.open().expect_ready()
    auth0_page.capture_authorize_url(login_page.start_sso)
    auth0_page.expect_provider_screen()

    user = sso_user()
    auth0_page.submit_identifier(user.email)
    auth0_page.password_input.or_(auth0_page.enterprise_error).wait_for(state="visible")

    if auth0_page.is_enterprise_directory_error():
        pytest.skip(
            "Auth0 STG only accepts enterprise-directory emails. The assignment "
            "account is a standard database user, so the password step never "
            "appears. Set SSO_EMAIL / SSO_PASSWORD to an enterprise user to "
            "finish this flow through to the app."
        )

    auth0_page.submit_password(user.password)
    dashboard_page.wait_until_loaded().expect_authenticated()
