from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache

from config.settings import env


@dataclass(frozen=True)
class BrowserSettings:
    """Google Chrome launch and context settings. No Playwright Chromium."""

    channel: str = "chrome"
    locale: str = "de-DE"
    viewport_width: int = 1280
    viewport_height: int = 720
    ignore_https_errors: bool = True
    default_timeout_ms: int = 12_000
    navigation_timeout_ms: int = 25_000
    launch_args: tuple[str, ...] = field(
        default_factory=lambda: (
            "--disable-extensions",
            "--disable-component-update",
            "--disable-background-networking",
            "--disable-sync",
            "--disable-default-apps",
            "--disable-popup-blocking",
            "--disable-translate",
            "--mute-audio",
            "--no-first-run",
            "--no-default-browser-check",
        )
    )

    def launch_options(self) -> dict:
        return {
            "channel": self.channel,
            "args": list(self.launch_args),
        }

    def context_options(self, base_url: str, basic_auth_username: str, basic_auth_password: str) -> dict:
        return {
            "base_url": base_url,
            "http_credentials": {
                "username": basic_auth_username,
                "password": basic_auth_password,
            },
            "ignore_https_errors": self.ignore_https_errors,
            "locale": self.locale,
            "viewport": {"width": self.viewport_width, "height": self.viewport_height},
        }


@lru_cache(maxsize=1)
def get_browser_settings() -> BrowserSettings:
    return BrowserSettings(
        channel=env("BROWSER_CHANNEL", "chrome"),
        locale=env("BROWSER_LOCALE", "de-DE"),
        default_timeout_ms=int(env("BROWSER_TIMEOUT_MS", "12000")),
        navigation_timeout_ms=int(env("BROWSER_NAVIGATION_TIMEOUT_MS", "25000")),
    )
