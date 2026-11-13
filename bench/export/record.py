"""The incident record: goodput's public data contract (ADR-0005).

One JSON line per incident. Every record joins what the system saw (the ``Incident`` and
the rules ``Verdict``) with what actually happened (the faultlab ledger), which is why this
module lives in ``bench`` (ADR-0004). The JSON Schema in ``docs/schemas/`` is generated
from these models (``make schemas``) and a CPU test fails if the two drift apart.

Scrubbing is enforced here rather than left to convention: node names must already be
pseudonyms (``n0``, ``n1``, ...), so a record that would leak a hostname fails validation.
"""

from __future__ import annotations

import re
from typing import Literal

from pydantic import Field, model_validator

from goodput.schemas import ComponentRef, Event, FaultClass, Provenance, Verdict
from goodput.schemas._base import SchemaModel, UtcNs

#: Version of the record contract. Bump on any breaking change and note it in the
#: dataset section of the model card.
RECORD_SCHEMA_V: Literal[1] = 1

NODE_PSEUDONYM_RE = re.compile(r"^n\d+$")


def render_event_line(event: Event) -> str:
    """Deterministic one-line text for an event (ADR-0005 contract).

    ``"<kind> " + " ".join(f"{k}={v}" for k, v in sorted(payload.items()))``. The node and
    rank are carried as payload by the exporter when they matter, so the rendering stays a
    pure function of ``kind`` and ``payload``.
    """
    parts = [event.kind, *(f"{k}={v}" for k, v in sorted(event.payload.items()))]
    return " ".join(parts)


class EventLine(SchemaModel):
    """One rendered event. ``ref`` is the ``event_id`` a verdict cites as evidence."""

    ref: str = Field(min_length=1, description="event_id; what Verdict.evidence cites")
    ts_utc_ns: UtcNs
    text: str = Field(min_length=1, description="render_event_line() output")


class GroundTruth(SchemaModel):
    """The answer, from the faultlab ledger. Never visible to the system under test."""

    fault_id: str = Field(pattern=r"^F\d{2}$", description="row in docs/FAULT_MATRIX.md")
    fault_class: FaultClass
    culprit: ComponentRef


class HardwareContext(SchemaModel):
    """Scrubbed environment from the run's env manifest: models and versions only.

    No hostnames, IPs, serials or GPU UUIDs.
    """

    num_nodes: int = Field(ge=1)
    gpus_per_node: int = Field(ge=1)
    gpu_model: str = Field(min_length=1)
    nic_model: str = Field(min_length=1)
    link_rate_gbps: float | None = Field(default=None, gt=0)
    fabric: Literal["infiniband", "roce", "other"]
    torch_version: str = Field(min_length=1)
    nccl_version: str = Field(min_length=1)
    cuda_version: str = Field(min_length=1)


class SplitKeys(SchemaModel):
    """Grouping keys for leakage-safe splits. Never split by random record."""

    run_id: str = Field(min_length=1)
    seed: int = Field(ge=0, description="fault-schedule seed of the run")
    topology_group: str = Field(min_length=1, description="held out as a unit")
    fault_family: str = Field(min_length=1, description="FAULT_MATRIX layer, e.g. NIC/fabric")


class IncidentRecord(SchemaModel):
    """One labelled incident, exactly as published (ADR-0005)."""

    schema_v: Literal[1] = RECORD_SCHEMA_V
    record_id: str = Field(min_length=1)
    incident_id: str = Field(min_length=1)
    events: tuple[EventLine, ...] = Field(min_length=1, description="time-ordered")
    labels: GroundTruth
    system_verdict: Verdict = Field(description="the rules classifier's verdict")
    provenance: Provenance = Field(description="of the fault, per ADR-0006")
    hardware: HardwareContext
    split_keys: SplitKeys

    @model_validator(mode="after")
    def _consistent(self) -> IncidentRecord:
        ts = [e.ts_utc_ns for e in self.events]
        if ts != sorted(ts):
            raise ValueError("events must be time-ordered")
        refs = [e.ref for e in self.events]
        if len(set(refs)) != len(refs):
            raise ValueError("event refs must be unique")
        if self.system_verdict.incident_id != self.incident_id:
            raise ValueError("system_verdict belongs to a different incident")
        missing = set(self.system_verdict.evidence) - set(refs)
        if missing:
            raise ValueError(f"verdict cites evidence not in the record: {sorted(missing)}")
        for who, ref in (
            ("labels.culprit", self.labels.culprit),
            ("system_verdict.culprit", self.system_verdict.culprit),
        ):
            if ref.node is not None and not NODE_PSEUDONYM_RE.match(ref.node):
                raise ValueError(f"{who}.node must be a pseudonym like 'n0', got {ref.node!r}")
            if ref.gpu_uuid is not None:
                raise ValueError(f"{who}.gpu_uuid must be scrubbed")
        return self
