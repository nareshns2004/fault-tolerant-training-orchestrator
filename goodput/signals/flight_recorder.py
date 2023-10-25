"""Cross-rank analysis of ProcessGroupNCCL flight-recorder dumps.

[OWNER-CORE] M3 — Naresh implements ``analyze``. Claude Code owns the fixtures and tests
(tests/fixtures/flight_recorder/, recorded from real dumps and labeled per rule 4).

Why this exists (INTERVIEW_DEFENSE.md Q4): on a hang every rank times out, so "first rank
to report" is not attribution. The culprit is the rank whose collective sequence differs:
it never *entered* seq N, never *completed* it, or entered a *different* op at seq N.

Parsing the dump format is version-specific; record the PyTorch version that produced
each fixture.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from enum import StrEnum

from pydantic import Field

from goodput.schemas._base import SchemaModel


class CollectiveState(StrEnum):
    SCHEDULED = "scheduled"
    STARTED = "started"
    COMPLETED = "completed"


class CollectiveRecord(SchemaModel):
    """One entry from one rank's flight-recorder ring buffer, normalized."""

    rank: int = Field(ge=0)
    process_group: str
    seq_id: int = Field(ge=0)
    op: str
    input_sizes: tuple[tuple[int, ...], ...] = ()
    dtype: str | None = None
    state: CollectiveState


class FindingKind(StrEnum):
    NEVER_ENTERED = "never_entered"
    NEVER_COMPLETED = "never_completed"
    DIVERGED = "diverged"  # op/size/dtype mismatch at the same seq -> desync (F04)


class RankFinding(SchemaModel):
    rank: int = Field(ge=0)
    process_group: str
    seq_id: int = Field(ge=0)
    kind: FindingKind


def analyze(
    records: Mapping[int, Sequence[CollectiveRecord]],
) -> tuple[RankFinding, ...]:
    """Align per-rank collective sequences and return the anomalous ranks.

    [OWNER-CORE] Not implemented by design. Tests in
    tests/unit/test_flight_recorder.py define the expected behaviour.
    """
    raise NotImplementedError("[OWNER-CORE] M3 — see module docstring")
