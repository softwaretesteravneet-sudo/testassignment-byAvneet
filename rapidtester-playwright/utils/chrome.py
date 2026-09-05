from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

from utils.logger import get_logger

log = get_logger("chrome")

_WINDOWS_CHROME_PATHS = (
    Path(os.environ.get("PROGRAMFILES", r"C:\Program Files"))
    / "Google"
    / "Chrome"
    / "Application"
    / "chrome.exe",
    Path(os.environ.get("PROGRAMFILES(X86)", r"C:\Program Files (x86)"))
    / "Google"
    / "Chrome"
    / "Application"
    / "chrome.exe",
    Path(os.environ.get("LOCALAPPDATA", ""))
    / "Google"
    / "Chrome"
    / "Application"
    / "chrome.exe",
)


def _registry_chrome() -> Path | None:
    if sys.platform != "win32":
        return None
    import winreg

    for hive in (winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE):
        try:
            with winreg.OpenKey(
                hive, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe"
            ) as key:
                value, _ = winreg.QueryValueEx(key, "")
        except OSError:
            continue
        path = Path(value)
        if path.is_file():
            return path
    return None


def find_google_chrome() -> Path | None:
    if sys.platform == "win32":
        registry = _registry_chrome()
        if registry:
            return registry
        for candidate in _WINDOWS_CHROME_PATHS:
            if candidate.is_file():
                return candidate
        which = shutil.which("chrome.exe") or shutil.which("chrome")
    else:
        which = (
            shutil.which("google-chrome")
            or shutil.which("google-chrome-stable")
            or shutil.which("chrome")
        )
    return Path(which) if which else None


def _install_chrome() -> None:
    log.info("Google Chrome is not installed. Installing...")
    if sys.platform == "win32" and shutil.which("winget"):
        result = subprocess.run(
            [
                "winget",
                "install",
                "--id",
                "Google.Chrome",
                "-e",
                "--accept-package-agreements",
                "--accept-source-agreements",
                "--disable-interactivity",
            ],
            check=False,
        )
        if result.returncode == 0 or find_google_chrome():
            return
    result = subprocess.run(
        [sys.executable, "-m", "playwright", "install", "chrome"],
        check=False,
    )
    if result.returncode != 0 and not find_google_chrome():
        raise RuntimeError("Could not install Google Chrome.")


def ensure_google_chrome() -> Path:
    """Reuse installed Chrome immediately. Install only when it is missing."""
    executable = find_google_chrome()
    if executable:
        log.info("Using Google Chrome: %s", executable)
        return executable
    _install_chrome()
    executable = find_google_chrome()
    if not executable:
        raise RuntimeError("Google Chrome is required but was not found after install.")
    log.info("Google Chrome is ready: %s", executable)
    return executable
