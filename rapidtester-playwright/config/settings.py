from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
import os

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")


def env(name: str, default: str = "") -> str:
    value = os.getenv(name, default)
    return value.strip() if value else default


def require_env(name: str) -> str:
    value = env(name)
    if not value:
        raise RuntimeError(
            f"Missing {name}. Copy .env.example to .env and fill it from the assignment PDF."
        )
    return value


@dataclass(frozen=True)
class Settings:
    """Environment and application URLs only. Users live in testdata/."""

    base_url: str
    app_url: str
    basic_auth_username: str
    basic_auth_password: str
    auth0_host: str
    auth0_client_id: str

    @property
    def login_url(self) -> str:
        return f"{self.base_url.rstrip('/')}/login"

    @property
    def customer_signup_url(self) -> str:
        return f"{self.base_url.rstrip('/')}/customer/signup"

    @property
    def sso_login_url(self) -> str:
        return f"{self.base_url.rstrip('/')}/sso/login"

    @property
    def sso_callback_url(self) -> str:
        return f"{self.base_url.rstrip('/')}/sso/callback"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings(
        base_url=env("BASE_URL", "https://auth.pre.stgrapidusertests.com"),
        app_url=env("APP_URL", "https://app.pre.stgrapidusertests.com"),
        basic_auth_username=require_env("BASIC_AUTH_USERNAME"),
        basic_auth_password=require_env("BASIC_AUTH_PASSWORD"),
        auth0_host=require_env("AUTH0_HOST"),
        auth0_client_id=require_env("AUTH0_CLIENT_ID"),
    )
