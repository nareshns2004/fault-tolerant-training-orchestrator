"""Declarative fault scenarios (ARCHITECTURE.md §3.6).

Safety invariants are encoded in the schema so an unsafe scenario fails at load time,
not at injection time (CLAUDE.md rule 5):
* every fault has a positive ``revert_timeout_s`` (watchdog auto-revert);
* destructive mechanisms must be opted into per fault with ``destructive: true``.
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Literal

import yaml
from pydantic import Field, model_validator

from goodput.schemas._base import SchemaModel


class TargetSelector(SchemaModel):
    """Resolved against ``artifacts/topology.json`` at run time. Exactly one field set,
    or ``random: true`` to draw a target from the scenario seed.
    """

    rank: int | None = Field(default=None, ge=0)
    node: str | None = None
    gpu_uuid: str | None = None
    nic: str | None = None
    random: bool = False

    @model_validator(mode="after")
    def _exactly_one(self) -> TargetSelector:
        chosen = [self.rank, self.node, self.gpu_uuid, self.nic]
        n = sum(v is not None for v in chosen) + int(self.random)
        if n != 1:
            raise ValueError("target must set exactly one of rank/node/gpu_uuid/nic/random")
        return self


class AtStep(SchemaModel):
    kind: Literal["step"] = "step"
    step: int = Field(ge=0)


class AfterSeconds(SchemaModel):
    kind: Literal["wall"] = "wall"
    after_s: float = Field(ge=0)


class Poisson(SchemaModel):
    """Arrivals with the given mean interval, drawn from the scenario seed (replayable)."""

    kind: Literal["poisson"] = "poisson"
    mtbf_s: float = Field(gt=0)


Trigger = Annotated[AtStep | AfterSeconds | Poisson, Field(discriminator="kind")]


class FaultSpec(SchemaModel):
    fault_id: str = Field(pattern=r"^F\d{2}$", description="row in docs/FAULT_MATRIX.md")
    target: TargetSelector
    trigger: Trigger
    duration_s: float | None = Field(default=None, gt=0, description="None = until reverted")
    revert_timeout_s: float = Field(gt=0, description="watchdog auto-revert deadline")
    destructive: bool = False

    @model_validator(mode="after")
    def _duration_within_timeout(self) -> FaultSpec:
        if self.duration_s is not None and self.duration_s > self.revert_timeout_s:
            raise ValueError("duration_s exceeds revert_timeout_s; the watchdog would fire")
        return self


class Scenario(SchemaModel):
    schema_v: Literal[1] = 1
    id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]*$")
    description: str = ""
    seed: int = Field(ge=0)
    faults: tuple[FaultSpec, ...] = Field(min_length=1)


def load_scenario(path: Path) -> Scenario:
    with path.open(encoding="utf-8") as fh:
        return Scenario.model_validate(yaml.safe_load(fh))
