from __future__ import annotations

from playwright.sync_api import expect

from pages.base_page import BasePage
from testdata.models import CustomerRegistrationData


class RegistrationPage(BasePage):
    def open(self) -> "RegistrationPage":
        self.goto(self.settings.customer_signup_url)
        self.wait_for_vue_app("create-account-button")
        return self

    @property
    def first_name_input(self):
        return self.test_id("first_name-input")

    @property
    def last_name_input(self):
        return self.test_id("last_name-input")

    @property
    def company_name_input(self):
        return self.test_id("company_name-input")

    @property
    def email_input(self):
        return self.test_id("email-input")

    @property
    def password_input(self):
        return self.test_id("password-input")

    @property
    def terms_checkbox(self):
        return self.test_id("terms-and-condition-checkbox")

    @property
    def submit_button(self):
        return self.test_id("create-account-button")

    @property
    def confirmation_resend_link(self):
        return self.test_id("resend-confirmation-email-link")

    def field_error(self, field_name: str):
        return self.test_id(f"{field_name}-error")

    def expect_ready(self) -> None:
        expect(self.submit_button).to_be_visible()
        expect(self.submit_button).to_be_disabled()

    def fill_form(self, data: CustomerRegistrationData) -> "RegistrationPage":
        self.log.info("Fill customer registration for %s", data.email)
        self.first_name_input.fill(data.first_name)
        self.last_name_input.fill(data.last_name)
        self.company_name_input.fill(data.company_name)
        self.email_input.fill(data.email)
        self.password_input.fill(data.password)
        self._set_terms(data.accept_terms)
        return self

    def submit(self) -> None:
        self.log.info("Submit customer registration")
        expect(self.submit_button).to_be_enabled()
        self.submit_button.click()

    def submit_and_expect_confirmation(self) -> None:
        self.submit()
        expect(self.confirmation_resend_link).to_be_visible()
        self.log.info("Registration confirmation is visible")

    def expect_field_error(self, field_name: str) -> None:
        self.log.info("Expect field error on %s", field_name)
        expect(self.field_error(field_name)).to_be_visible()

    def expect_error_after_clearing(self, field_name: str, locator, restore_value: str) -> None:
        self.log.info("Clear %s and expect a validation error", field_name)
        locator.fill("")
        self.submit()
        self.expect_field_error(field_name)
        locator.fill(restore_value)

    def _set_terms(self, accept: bool) -> None:
        checked = self.terms_checkbox.is_checked()
        if accept and not checked:
            self.terms_checkbox.check()
        elif not accept and checked:
            self.terms_checkbox.uncheck()
