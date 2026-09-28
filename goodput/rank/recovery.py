"""In-process recovery entry points (ARCHITECTURE.md §3.1).

[OWNER-CORE] M5 — Naresh implements. This module fixes the interface only.

Before implementing, be able to answer (INTERVIEW_DEFENSE.md Q6, Q17):
* What state is a ProcessGroupNCCL communicator in after an async error or abort, and
  which operations are still legal on it?
* When is the CUDA context itself poisoned (sticky errors) so the process must exit?
* How does FSDP2's DeviceMesh get rebuilt after membership changes?
"""

from __future__ import annotations

from typing import Protocol

from goodput.schemas import Tier


class RecoveryHooks(Protocol):
    def abort_and_reinit_comms(self) -> None:
        """Abort all communicators in this process and re-create them for the current world."""
        ...

    def restore(self, tier: Tier) -> int:
        """Restore model/optimizer/dataloader/RNG state from ``tier``; return restored step."""
        ...

    def rebuild_mesh(self, world_size: int) -> None:
        """Rebuild the device mesh for a new world size (node replacement or shrink)."""
        ...
