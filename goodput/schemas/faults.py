"""Ground-truth record of a fault injection, written by faultlab's ledger."""

from __future__ import annotations

from typing import Literal

from pydantic import Field, model_validator

from goodput.schemas._base import SchemaModel, UtcNs
from goodput.schemas.common import ComponentRef, FaultClass, Provenance


class FaultInjection(SchemaModel):
    """One injected (or harvested) fault. The evaluator's source of truth.

    ``t_start_utc_ns`` is ``t_fault`` in EVALUATION.md §1. For harvested real faults it
    is the earliest evidence event, and ``scenario_id`` is ``None``.
    """

    schema_v: Literal[1] = 1
    id: str = Field(min_length=1)
    fault_id: str = Field(pattern=r"^F\d{2}$", description="row in docs/FAULT_MATRIX.md")
    fault_class: FaultClass
    label: Provenance
    target: ComponentRef
    mechanism: str = Field(min_length=1)
    scenario_id: str | None = None
    t_start_utc_ns: UtcNs
    t_end_utc_ns: UtcNs | None = None
    revert_ok: bool | None = Field(
        default=None, description="None = no revert needed or not yet attempted"
    )

    @model_validator(mode="after")
    def _ordered(self) -> FaultInjection:
        if self.t_end_utc_ns is not None and self.t_end_utc_ns < self.t_start_utc_ns:
            raise ValueError("t_end_utc_ns precedes t_start_utc_ns")
        if self.fault_class is FaultClass.UNKNOWN:
            raise ValueError("ground truth cannot be 'unknown'")
        return self
