"""Incidents (correlated evidence) and Verdicts (classified, attributed incidents)."""

from __future__ import annotations

from typing import Literal

from pydantic import Field, model_validator

from goodput.schemas._base import SchemaModel, UtcNs
from goodput.schemas.common import ComponentRef, FaultClass
from goodput.schemas.events import Event
from goodput.schemas.topology import Topology


class Incident(SchemaModel):
    """A trigger plus every event in its correlation window, joined against topology."""

    schema_v: Literal[1] = 1
    id: str = Field(min_length=1)
    trigger_event: Event
    window_start_utc_ns: UtcNs
    window_end_utc_ns: UtcNs
    events: tuple[Event, ...]
    topology_slice: Topology

    @model_validator(mode="after")
    def _window(self) -> Incident:
        if self.window_end_utc_ns < self.window_start_utc_ns:
            raise ValueError("window end precedes start")
        return self


class Verdict(SchemaModel):
    """Classifier output. No recovery action may be taken without one (ARCHITECTURE §1.2)."""

    schema_v: Literal[1] = 1
    incident_id: str = Field(min_length=1)
    fault_class: FaultClass
    culprit: ComponentRef
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: tuple[str, ...] = Field(description="event_ids from the incident")
    classifier_version: str = Field(min_length=1)

    @model_validator(mode="after")
    def _evidence_required(self) -> Verdict:
        if self.fault_class is not FaultClass.UNKNOWN and not self.evidence:
            raise ValueError("a non-'unknown' verdict must cite evidence")
        return self
