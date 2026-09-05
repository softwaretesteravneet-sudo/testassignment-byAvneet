import pytest

from pages.registration_page import RegistrationPage
from testdata.customers import INVALID_EMAIL, WEAK_PASSWORD, unique_customer


@pytest.mark.smoke
@pytest.mark.registration
def test_customer_registration_submits_form(
    registration_page: RegistrationPage,
) -> None:
    registration_page.open().expect_ready()
    registration_page.fill_form(unique_customer()).submit_and_expect_confirmation()


@pytest.mark.registration
def test_customer_registration_field_validation(
    registration_page: RegistrationPage,
) -> None:
    page = registration_page.open()
    page.expect_ready()

    customer = unique_customer()
    page.first_name_input.fill(customer.first_name)
    page.last_name_input.fill(customer.last_name)
    page.company_name_input.fill(customer.company_name)
    page.email_input.fill(customer.email)
    assert not page.submit_button.is_enabled()

    page.password_input.fill(customer.password)
    assert not page.submit_button.is_enabled()
    page.terms_checkbox.check()
    assert page.submit_button.is_enabled()

    page.expect_error_after_clearing("first_name", page.first_name_input, customer.first_name)
    page.expect_error_after_clearing("last_name", page.last_name_input, customer.last_name)
    page.expect_error_after_clearing("company_name", page.company_name_input, customer.company_name)
    page.expect_error_after_clearing("email", page.email_input, customer.email)

    page.email_input.fill(INVALID_EMAIL)
    page.submit()
    page.expect_field_error("email")
    page.email_input.fill(customer.email)

    page.password_input.fill(WEAK_PASSWORD)
    page.submit()
    page.expect_field_error("password")
