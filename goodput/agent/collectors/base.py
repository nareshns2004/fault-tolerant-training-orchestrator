"""Collector interface shared by DCGM, RDMA-counter, kernel-log, and host collectors."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from goodput.schemas import TelemetrySample


class Collector(Protocol):
    """A source of telemetry on one node.

    Counter names are *discovered*, never hardcoded: RDMA ``hw_counters`` differ by
    driver and firmware (FAULT_MATRIX.md gotchas). ``discover`` runs once at startup
    and its result is recorded in the env manifest.

    RDMA counter semantics and anomaly rules are [OWNER-CORE] (M4).
    """

    name: str

    def discover(self) -> Sequence[str]:
        """Return the metric names this collector can read on this host."""
        ...

    def sample(self) -> Sequence[TelemetrySample]:
        """Read all discovered metrics once. Must be cheap enough to run every second."""
        ...
