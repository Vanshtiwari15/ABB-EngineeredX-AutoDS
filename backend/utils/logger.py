"""Structured logging with correlation IDs.

Every log record carries a ``correlation_id`` field derived from a
:class:`contextvars.ContextVar`. The middleware in :mod:`backend.main` sets this
for each request so all downstream logs are traceable.
"""

from __future__ import annotations

import logging
import sys
from contextvars import ContextVar
from logging.handlers import RotatingFileHandler
from typing import Any

from pythonjsonlogger import jsonlogger

from backend.core.config import Settings, get_settings

_correlation_id: ContextVar[str] = ContextVar("correlation_id", default="-")

_LOGGING_CONFIGURED = False


def set_correlation_id(value: str) -> None:
    _correlation_id.set(value)


def get_correlation_id() -> str:
    return _correlation_id.get()


class _CorrelationFilter(logging.Filter):
    """Inject the current correlation_id into every log record."""

    def filter(self, record: logging.LogRecord) -> bool:  # noqa: D401
        record.correlation_id = _correlation_id.get()
        return True


class _JsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(
        self,
        log_record: dict[str, Any],
        record: logging.LogRecord,
        message_dict: dict[str, Any],
    ) -> None:
        super().add_fields(log_record, record, message_dict)
        log_record.setdefault("level", record.levelname)
        log_record.setdefault("logger", record.name)
        log_record.setdefault("correlation_id", getattr(record, "correlation_id", "-"))


def _build_console_handler(settings: Settings) -> logging.Handler:
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.addFilter(_CorrelationFilter())
    if settings.log_json:
        handler.setFormatter(
            _JsonFormatter(
                "%(asctime)s %(level)s %(logger)s %(correlation_id)s %(message)s"
            )
        )
    else:
        handler.setFormatter(
            logging.Formatter(
                fmt=(
                    "%(asctime)s | %(levelname)-8s | %(name)s | "
                    "cid=%(correlation_id)s | %(message)s"
                )
            )
        )
    return handler


def _build_file_handler(settings: Settings) -> logging.Handler:
    settings.logs_dir.mkdir(parents=True, exist_ok=True)
    handler = RotatingFileHandler(
        settings.logs_dir / settings.log_file,
        maxBytes=settings.log_max_bytes,
        backupCount=settings.log_backup_count,
        encoding="utf-8",
    )
    handler.addFilter(_CorrelationFilter())
    handler.setFormatter(
        _JsonFormatter(
            "%(asctime)s %(level)s %(logger)s %(correlation_id)s %(message)s"
        )
    )
    return handler


def configure_logging(settings: Settings | None = None) -> None:
    """Configure global logging once. Safe to call multiple times."""
    global _LOGGING_CONFIGURED
    if _LOGGING_CONFIGURED:
        return
    settings = settings or get_settings()
    root = logging.getLogger()
    root.setLevel(settings.log_level.upper())
    # Wipe pre-existing handlers to avoid duplicate logs (e.g. uvicorn).
    for h in list(root.handlers):
        root.removeHandler(h)
    root.addHandler(_build_console_handler(settings))
    root.addHandler(_build_file_handler(settings))
    # Tone down noisy loggers.
    for noisy in ("uvicorn.access", "uvicorn.error", "watchfiles"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
    _LOGGING_CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    """Return a configured logger."""
    if not _LOGGING_CONFIGURED:
        configure_logging()
    return logging.getLogger(name)
