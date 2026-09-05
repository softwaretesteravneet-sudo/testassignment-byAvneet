from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import parse_qs, urlparse

from playwright.sync_api import expect

from pages.base_page import BasePage
from testdata.sso import AUTH0_PKCE_METHOD, AUTH0_RESPONSE_MODE, AUTH0_RESPONSE_TYPE, AUTH0_SCOPES


@dataclass(frozen=True)
class Auth0AuthorizeRequest:
    url: str
    client_id: str
    redirect_uri: str
    response_type: str
    response_mode: str
    scope: str
    state: str
    nonce: str
    code_challenge: str
    code_challenge_method: str

    @classmethod
    def from_url(cls, url: str) -> "Auth0AuthorizeRequest":
        params = {key: values[0] for key, values in parse_qs(urlparse(url).query).items()}
        required = (
            "client_id",
            "redirect_uri",
            "response_type",
            "response_mode",
            "scope",
            "state",
            "nonce",
            "code_challenge",
            "code_challenge_method",
        )
        missing = [name for name in required if not params.get(name)]
        if missing:
            raise AssertionError(f"Auth0 /authorize is missing {missing}: {url}")
        return cls(url=url, **{name: params[name] for name in required})


class Auth0Page(BasePage):
    """Auth0 Universal Login — the external SSO provider for Rapidusertests STG."""

    @property
    def email_input(self):
        return self.page.locator("#username")

    @property
    def password_input(self):
        return self.page.locator("#password")

    @property
    def continue_button(self):
        return self.page.get_by_role("button", name="Continue")

    @property
    def enterprise_error(self):
        return self.page.get_by_text("Email does not match any enterprise directory")

    def wait_until_loaded(self) -> "Auth0Page":
        self.page.wait_for_url(f"**{self.settings.auth0_host}/**")
        expect(self.email_input).to_be_visible()
        expect(self.continue_button).to_be_visible()
        return self

    def capture_authorize_url(self, start_sso) -> Auth0AuthorizeRequest:
        with self.page.expect_request(
            lambda request: self.settings.auth0_host in request.url and "/authorize" in request.url,
            timeout=self.browser_settings.navigation_timeout_ms,
        ) as pending:
            start_sso()
        self.wait_until_loaded()
        authorize = Auth0AuthorizeRequest.from_url(pending.value.url)
        self.log.info("Auth0 /authorize captured")
        return authorize

    def expect_provider_screen(self) -> None:
        expect(self.page).to_have_title("Log in | RapidUsertests STG")
        expect(self.page.get_by_role("heading", name="Welcome")).to_be_visible()
        expect(self.email_input).to_be_visible()
        self.log.info("Auth0 provider screen is visible")

    def expect_authorize_contract(self, authorize: Auth0AuthorizeRequest) -> None:
        parsed = urlparse(authorize.url)
        assert parsed.scheme == "https"
        assert parsed.netloc == self.settings.auth0_host
        assert parsed.path == "/authorize"
        assert authorize.client_id == self.settings.auth0_client_id
        assert authorize.redirect_uri == self.settings.sso_callback_url
        assert authorize.response_type == AUTH0_RESPONSE_TYPE
        assert authorize.response_mode == AUTH0_RESPONSE_MODE
        assert authorize.code_challenge_method == AUTH0_PKCE_METHOD
        assert authorize.code_challenge
        assert authorize.state
        assert authorize.nonce
        for scope in AUTH0_SCOPES:
            assert scope in authorize.scope.split()
        self.log.info("Auth0 /authorize contract is valid")

    def submit_identifier(self, email: str) -> None:
        self.log.info("Submit Auth0 identifier %s", email)
        self.email_input.fill(email)
        self.continue_button.click()

    def submit_password(self, password: str) -> None:
        self.log.info("Submit Auth0 password")
        self.password_input.wait_for(state="visible")
        self.password_input.fill(password)
        self.continue_button.click()

    def login(self, email: str, password: str) -> None:
        self.submit_identifier(email)
        expect(self.password_input.or_(self.enterprise_error)).to_be_visible()
        if self.enterprise_error.is_visible():
            raise AssertionError(
                "Auth0 rejected the identifier because it is not in an enterprise "
                "directory. This tenant only accepts emails in a configured IdP."
            )
        self.submit_password(password)

    def is_enterprise_directory_error(self) -> bool:
        visible = self.enterprise_error.is_visible()
        if visible:
            self.log.warning("Auth0 rejected the identifier: not in an enterprise directory")
        return visible
