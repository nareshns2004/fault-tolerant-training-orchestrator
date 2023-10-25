"""Recovery actions issued by the policy engine."""

from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import Field, model_validator

from goodput.schemas._base import SchemaModel, UtcNs
from goodput.schemas.common import ComponentRef, Tier


class ActionKind(StrEnum):
    """Ordered roughly by blast radius, smallest first."""

    REINIT_COMM = "reinit_comm"
    RESTART_RANKS = "restart_ranks"
    REPLACE_NODE = "replace_node"
    SHRINK = "shrink"
    ROLLBACK = "rollback"
    HALT = "halt"


class ActionOutcome(StrEnum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    ABORTED = "aborted"


class Action(SchemaModel):
    schema_v: Literal[1] = 1
    id: str = Field(min_length=1)
    verdict_id: str = Field(min_length=1)
    kind: ActionKind
    targets: tuple[ComponentRef, ...]
    restore_tier: Tier | None = None
    started_utc_ns: UtcNs | None = None
    finished_utc_ns: UtcNs | None = None
    outcome: ActionOutcome = ActionOutcome.PENDING

    @model_validator(mode="after")
    def _consistent(self) -> Action:
        if self.finished_utc_ns is not None:
            if self.started_utc_ns is None:
                raise ValueError("finished without started")
            if self.finished_utc_ns < self.started_utc_ns:
                raise ValueError("finished precedes started")
        if self.outcome is not ActionOutcome.PENDING and self.finished_utc_ns is None:
            raise ValueError("terminal outcome requires finished_utc_ns")
        return self
