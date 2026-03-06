"""Structured logging system - per run."""

import logging
import sys
from pathlib import Path

import structlog


def setup_logging(run_folder: Path | None = None, log_level: str = "INFO") -> None:
    """
    Configure structured logging for the run.

    Logs to stdout. Optionally writes to {run_folder}/run.log.

    Args:
        run_folder: Optional path to run folder for file logging.
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR).
    """
    level = getattr(logging, log_level.upper())
    shared_processors: list = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]
    renderer = (
        structlog.dev.ConsoleRenderer()
        if sys.stderr.isatty()
        else structlog.processors.JSONRenderer()
    )
    structlog.configure(
        processors=shared_processors + [renderer],
        wrapper_class=structlog.make_filtering_bound_logger(level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Also configure stdlib logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )

    if run_folder:
        log_path = run_folder / "run.log"
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setFormatter(logging.Formatter("%(message)s"))
        logging.getLogger().addHandler(file_handler)
