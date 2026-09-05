from __future__ import annotations

from playwright.sync_api import expect

from pages.base_page import BasePage
from testdata.models import User


class LoginPage(BasePage):
    def open(self) -> "LoginPage":
        self.goto(self.settings.login_url)
        self.wait_for_vue_app("login-button")
        return self

    @property
    def email_input(self):
        return self.test_id("email-input")

    @property
    def password_input(self):
        return self.test_id("password-input")

    @property
    def login_button(self):
        return self.test_id("login-button")

    @property
    def sso_login_link(self):
        return self.test_id("sso-login-link")

    def expect_ready(self) -> None:
        expect(self.login_button).to_be_visible()
        expect(self.sso_login_link).to_be_visible()

    def login(self, user: User) -> None:
        self.log.info("Standard login as %s", user.email)
        self.email_input.fill(user.email)
        self.password_input.fill(user.password)
        self.login_button.click()

    def start_sso(self) -> None:
        self.log.info("Start SSO from the login page")
        self.sso_login_link.click()
