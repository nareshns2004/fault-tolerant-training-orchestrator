from __future__ import annotations

import json
import logging

import pytest

from goodput.logs import JsonFormatter


def test_json_formatter_merges_extra() -> None:
    rec = logging.LogRecord("goodput.x", logging.INFO, __file__, 1, "hello %s", ("w",), None)
    rec.rank = 3
    out = json.loads(JsonFormatter().format(rec))
    assert out["msg"] == "hello w"
    assert out["rank"] == 3
    assert out["level"] == "INFO"
    assert isinstance(out["ts_utc_ns"], int)


@pytest.mark.parametrize("name", ["goodput.agent", "agent"])
def test_logger_namespace(name: str) -> None:
    from goodput.logs import get_logger

    assert get_logger(name).name == "goodput.agent"
