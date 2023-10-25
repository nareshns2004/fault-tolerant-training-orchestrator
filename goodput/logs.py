"""Structured JSON logging. ``goodput`` code never uses ``print`` (CLAUDE.md conventions)."""

from __future__ import annotations

import json
import logging
import sys
import time
from typing import Any, ClassVar

_RESERVED = frozenset(vars(logging.makeLogRecord({})))


class JsonFormatter(logging.Formatter):
    """One JSON object per line; ``extra={...}`` fields are merged in as top-level keys."""

    default_keys: ClassVar[tuple[str, ...]] = ("ts_utc_ns", "level", "logger", "msg")

    def format(self, record: logging.LogRecord) -> str:
        out: dict[str, Any] = {
            "ts_utc_ns": int(record.created * 1e9),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        for k, v in record.__dict__.items():
            if k not in _RESERVED and k not in out:
                out[k] = v
        if record.exc_info:
            out["exc"] = self.formatException(record.exc_info)
        return json.dumps(out, default=str, separators=(",", ":"))


def get_logger(name: str) -> logging.Logger:
    """Return a logger under the ``goodput`` hierarchy."""
    return logging.getLogger(name if name.startswith("goodput") else f"goodput.{name}")


def configure(level: int | str = logging.INFO) -> None:
    """Install the JSON handler on the ``goodput`` root logger. Idempotent."""
    root = logging.getLogger("goodput")
    root.setLevel(level)
    if not any(isinstance(h.formatter, JsonFormatter) for h in root.handlers):
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(JsonFormatter())
        root.addHandler(handler)
    root.propagate = False
    logging.Formatter.converter = time.gmtime
