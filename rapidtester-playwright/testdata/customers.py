from __future__ import annotations

from uuid import uuid4

from faker import Faker

from testdata.models import CustomerRegistrationData

_fake = Faker()

VALID_PASSWORD = "Fakedata44336!"
WEAK_PASSWORD = "short"
INVALID_EMAIL = "not-an-email"


def unique_customer() -> CustomerRegistrationData:
    """Unique payload so parallel workers never share an email."""
    token = uuid4().hex[:10]
    return CustomerRegistrationData(
        first_name=_fake.first_name(),
        last_name=_fake.last_name(),
        company_name=f"RapidTester {token}",
        email=f"your.email+rt{token}@gmail.com",
        password=VALID_PASSWORD,
        accept_terms=True,
    )
