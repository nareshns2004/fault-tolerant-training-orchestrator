"""Mechanism interface.

[OWNER-CORE] M2 — the revert/watchdog design is Naresh's. This is a proposed shape:
injection is split into ``prepare`` and ``apply`` so the revert exists and can be
registered with the watchdog *before* anything on the host changes.
"""

from __future__ import annotations

from typing import Protocol

from goodput.schemas import ComponentRef, Provenance


class PreparedFault(Protocol):
    def apply(self) -> None:
        """Change host state. Only called after ``revert`` has been registered."""
        ...

    def revert(self) -> bool:
        """Undo ``apply``. Idempotent; safe to call if ``apply`` never ran. True on success."""
        ...


class Mechanism(Protocol):
    name: str
    label: Provenance
    destructive: bool

    def prepare(self, target: ComponentRef) -> PreparedFault: ...
