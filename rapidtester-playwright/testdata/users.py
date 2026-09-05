from __future__ import annotations

from config.settings import env, require_env
from testdata.models import User


def standard_user() -> User:
    return User(
        email=require_env("LOGIN_EMAIL"),
        password=require_env("LOGIN_PASSWORD"),
    )


def sso_user() -> User:
    login = standard_user()
    return User(
        email=env("SSO_EMAIL") or login.email,
        password=env("SSO_PASSWORD") or login.password,
    )
