"""Job state machine (ARCHITECTURE.md §3.3).

[OWNER-CORE] M5 — Naresh implements the transition rules. Every transition must be
emitted as an ``Event(kind="state.transition")``; MTTD and MTTR are computed from those
events and nothing else (EVALUATION.md §1).
"""

from __future__ import annotations

from typing import Protocol

from goodput.schemas import Event, JobState


class JobStateMachine(Protocol):
    @property
    def state(self) -> JobState: ...

    def on_event(self, event: Event) -> tuple[Event, ...]:
        """Consume one event; return the transition events it caused (possibly none)."""
        ...
