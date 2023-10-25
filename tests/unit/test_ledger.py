from __future__ import annotations

from pathlib import Path

import pytest

from faultlab.ledger import Ledger
from goodput.schemas import ComponentRef, FaultClass, FaultInjection, Provenance


def _rec(**kw: object) -> FaultInjection:
    base: dict[str, object] = dict(
        id="f1",
        fault_id="F08",
        fault_class=FaultClass.NIC_LINK_DOWN,
        label=Provenance.INDUCED,
        target=ComponentRef(node="n0", nic="dev0", port=1),
        mechanism="ip-link-down",
        t_start_utc_ns=100,
    )
    base.update(kw)
    return FaultInjection.model_validate(base)


def test_last_record_wins_and_sweep_finds_unreverted(tmp_path: Path) -> None:
    ledger = Ledger(tmp_path / "ledger.jsonl")
    ledger.append(_rec())
    ledger.append(_rec(id="f2"))
    ledger.append(_rec(t_end_utc_ns=200, revert_ok=True))
    latest = ledger.latest()
    assert latest["f1"].revert_ok is True
    assert [r.id for r in ledger.unreverted()] == ["f2"]


def test_corrupt_line_is_reported_with_location(tmp_path: Path) -> None:
    p = tmp_path / "ledger.jsonl"
    p.write_text('{"not": "a record"}\n', encoding="utf-8")
    with pytest.raises(ValueError, match=r"ledger.jsonl:1"):
        list(Ledger(p).records())


def test_missing_ledger_is_empty(tmp_path: Path) -> None:
    assert Ledger(tmp_path / "none.jsonl").latest() == {}
