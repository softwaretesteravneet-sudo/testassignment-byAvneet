from __future__ import annotations

from config.settings import env
from testdata.models import User


def standard_user() -> User:
    return User(
        email=env("LOGIN_EMAIL", "your.email+fakedata44336@gmail.com"),
        password=env("LOGIN_PASSWORD", "fakedata44336!"),
    )


def sso_user() -> User:
    login = standard_user()
    return User(
        email=env("SSO_EMAIL") or login.email,
        password=env("SSO_PASSWORD") or login.password,
    )
