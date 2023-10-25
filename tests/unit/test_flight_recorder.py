"""Behavioural spec for the [OWNER-CORE] cross-rank analyzer (M3).

These cases are hand-built and therefore SYNTHETIC (rule 4). They pin down the intended
semantics; recorded real dumps go in tests/fixtures/flight_recorder/ as M3 lands.
xfail(strict=True) flips to a failure the moment ``analyze`` is implemented, so they
must then be un-marked rather than silently passing.
"""

from __future__ import annotations

import pytest

from goodput.signals.flight_recorder import (
    CollectiveRecord,
    CollectiveState,
    FindingKind,
    analyze,
)

pytestmark = pytest.mark.xfail(raises=NotImplementedError, strict=True, reason="[OWNER-CORE] M3")

PG = "default_pg"


def _r(rank: int, seq: int, state: CollectiveState, op: str = "allreduce") -> CollectiveRecord:
    return CollectiveRecord(
        rank=rank, process_group=PG, seq_id=seq, op=op, input_sizes=((1024,),), state=state
    )


def _healthy(rank: int, upto: int) -> list[CollectiveRecord]:
    return [_r(rank, s, CollectiveState.COMPLETED) for s in range(upto)]


def test_rank_that_never_entered_is_the_culprit() -> None:
    # F03-like: rank 2 stuck outside collectives; peers started seq 5 and are waiting.
    recs = {r: [*_healthy(r, 5), _r(r, 5, CollectiveState.STARTED)] for r in (0, 1, 3)}
    recs[2] = _healthy(2, 5)
    findings = analyze(recs)
    assert [(f.rank, f.seq_id, f.kind) for f in findings] == [(2, 5, FindingKind.NEVER_ENTERED)]


def test_all_started_none_completed_is_not_blamed_on_first_reporter() -> None:
    # F02-like with no distinguishing FR evidence: analyzer must not invent a culprit
    # (progress beacons / telemetry break the tie, not "first to time out").
    recs = {r: [*_healthy(r, 5), _r(r, 5, CollectiveState.STARTED)] for r in range(4)}
    assert all(f.kind is FindingKind.NEVER_COMPLETED for f in analyze(recs))


def test_op_mismatch_at_same_seq_is_desync() -> None:
    recs = {r: [*_healthy(r, 5), _r(r, 5, CollectiveState.STARTED)] for r in range(4)}
    recs[1][-1] = _r(1, 5, CollectiveState.STARTED, op="allgather")
    findings = analyze(recs)
    assert any(f.rank == 1 and f.kind is FindingKind.DIVERGED for f in findings)
