"""Enforce ADR-0004 package boundaries.

``goodput`` (system under test) must not see ``faultlab`` (ground truth) or ``bench``
(evaluator); ``faultlab`` may use only ``goodput.schemas``.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def _imports(pkg: str) -> list[tuple[Path, str]]:
    found: list[tuple[Path, str]] = []
    for path in (ROOT / pkg).rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                found += [(path, a.name) for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                found.append((path, node.module))
    return found


@pytest.mark.parametrize("forbidden", ["faultlab", "bench"])
def test_goodput_does_not_import(forbidden: str) -> None:
    bad = [(p, m) for p, m in _imports("goodput") if m.split(".")[0] == forbidden]
    assert not bad, f"goodput imports {forbidden}: {bad}"


def test_faultlab_uses_only_goodput_schemas() -> None:
    bad = [
        (p, m)
        for p, m in _imports("faultlab")
        if m.split(".")[0] in {"goodput", "bench"} and not m.startswith("goodput.schemas")
    ]
    assert not bad, f"faultlab reaches beyond goodput.schemas: {bad}"


def test_core_importable_without_torch() -> None:
    offenders = [
        (p, m)
        for p, m in _imports("goodput")
        if m.split(".")[0] == "torch" and "rank" not in p.parts and "ckpt" not in p.parts
    ]
    assert not offenders, f"torch imported outside rank/ckpt: {offenders}"
