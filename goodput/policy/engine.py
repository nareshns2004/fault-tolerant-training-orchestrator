"""Policy interface (ARCHITECTURE.md §3.3, FAULT_MATRIX.md 'Recovery action' column)."""

from __future__ import annotations

from typing import Protocol

from goodput.schemas import Action, Topology, Verdict


class Policy(Protocol):
    def decide(self, verdict: Verdict, topology: Topology) -> Action | None:
        """Map a verdict to the smallest-blast-radius action, or ``None`` (alert only).

        Guards (max restarts per window, spare capacity, escalation) apply here. Never
        cordon on ``collective_desync``, ``fabric_congestion`` or ``gpu_oom``.
        """
        ...
