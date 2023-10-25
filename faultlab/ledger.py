"""Append-only ground-truth ledger of ``FaultInjection`` records (JSON Lines).

A fault is written at injection start and again when it ends or is reverted; the last
record for an ``id`` wins. Every write is flushed and fsynced so a harness crash cannot
lose a fault that already happened — an injected fault missing from the ledger would
become a false "real" fault in the dataset.
"""

from __future__ import annotations

import os
from collections.abc import Iterator
from pathlib import Path

from goodput.schemas import FaultInjection


class Ledger:
    def __init__(self, path: Path) -> None:
        self.path = path

    def append(self, record: FaultInjection) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        line = record.model_dump_json() + "\n"
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(line)
            fh.flush()
            os.fsync(fh.fileno())

    def records(self) -> Iterator[FaultInjection]:
        if not self.path.exists():
            return
        with self.path.open(encoding="utf-8") as fh:
            for lineno, line in enumerate(fh, start=1):
                if not line.strip():
                    continue
                try:
                    yield FaultInjection.model_validate_json(line)
                except ValueError as exc:
                    raise ValueError(f"{self.path}:{lineno}: corrupt ledger record") from exc

    def latest(self) -> dict[str, FaultInjection]:
        """Current state of every fault, keyed by id."""
        return {r.id: r for r in self.records()}

    def unreverted(self) -> list[FaultInjection]:
        """Faults with no successful revert — input to the startup revert sweep."""
        return [r for r in self.latest().values() if r.revert_ok is False or r.t_end_utc_ns is None]
