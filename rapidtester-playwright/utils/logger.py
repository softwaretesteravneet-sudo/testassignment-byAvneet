from __future__ import annotations

import logging
import os
from pathlib import Path

LOGGER_NAME = "rapidtester"


class _WorkerFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.worker = os.environ.get("PYTEST_XDIST_WORKER", "master")
        return True


def get_logger(name: str | None = None) -> logging.Logger:
    if name:
        return logging.getLogger(f"{LOGGER_NAME}.{name}")
    return logging.getLogger(LOGGER_NAME)


def configure_logging(execution_dir: Path) -> Path:
    """Write DEBUG to suite.log and INFO+ to the console for this run."""
    log_path = Path(execution_dir) / "suite.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    resolved = str(log_path.resolve())

    logger = get_logger()
    logger.setLevel(logging.DEBUG)
    logger.propagate = True

    if any(getattr(handler, "baseFilename", None) == resolved for handler in logger.handlers):
        return log_path

    formatter = logging.Formatter(
        "%(asctime)s | %(worker)s | %(levelname)-7s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    worker_filter = _WorkerFilter()

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    file_handler.addFilter(worker_filter)

    logger.addHandler(file_handler)
    logger.propagate = True
    logger.debug("Suite logging started: %s", log_path)
    return log_path
