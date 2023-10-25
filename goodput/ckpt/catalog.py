"""Checkpoint catalog: the only authority on which checkpoints are valid."""

from __future__ import annotations

from typing import Protocol

from goodput.schemas import CheckpointManifest, Tier


class CheckpointCatalog(Protocol):
    """Atomic-commit catalog. Readers ignore any shard set without a committed manifest."""

    def commit(self, manifest: CheckpointManifest) -> None: ...

    def latest(self, tier: Tier) -> CheckpointManifest | None: ...

    def verify(self, manifest: CheckpointManifest) -> bool:
        """Recompute shard checksums; ``False`` means fall back (F15)."""
        ...
