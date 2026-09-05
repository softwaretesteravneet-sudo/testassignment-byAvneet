from __future__ import annotations

from datetime import datetime
from pathlib import Path

REPORTS_ROOT = Path("reports")


def new_execution_dir(now: datetime | None = None) -> Path:
    """reports/<date>/<time> — one folder per run, grouped by calendar day."""
    stamp = now or datetime.now()
    return REPORTS_ROOT / stamp.strftime("%Y-%m-%d") / stamp.strftime("%H-%M-%S")


def apply_report_paths(config, execution_dir: Path) -> Path:
    """Point pytest-html and Playwright artifacts at the same execution folder."""
    artifacts_dir = execution_dir / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    config.option.htmlpath = str(execution_dir / "report.html")
    config.option.self_contained_html = True
    config.option.output = str(artifacts_dir)
    config.execution_report_dir = str(execution_dir)
    config.suite_log_path = str(execution_dir / "suite.log")
    return execution_dir
