"""Events and telemetry — the raw material every metric is computed from."""

from __future__ import annotations

import re
import uuid
from typing import Literal

from pydantic import Field, JsonValue, field_validator

from goodput.schemas._base import MonoNs, SchemaModel, UtcNs
from goodput.schemas.common import EntityKind, Provenance

_KIND_RE = re.compile(r"^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+$")


class Event(SchemaModel):
    """Anything that happened: a state transition, anomaly, verdict, action phase.

    ``kind`` is a dotted namespace (``state.transition``, ``liveness.hung``,
    ``fabric.port_state``) so consumers can filter by prefix without a central enum
    that every collector has to edit.
    """

    schema_v: Literal[1] = 1
    event_id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    ts_utc_ns: UtcNs
    ts_mono_ns: MonoNs
    source: str = Field(min_length=1, description="emitting component, e.g. agent/nic")
    node: str = Field(min_length=1)
    rank: int | None = Field(default=None, ge=0)
    kind: str
    payload: dict[str, JsonValue] = Field(default_factory=dict)

    @field_validator("kind")
    @classmethod
    def _dotted_kind(cls, v: str) -> str:
        if not _KIND_RE.match(v):
            raise ValueError(f"kind must be dotted lowercase (e.g. 'state.transition'): {v!r}")
        return v


class TelemetrySample(SchemaModel):
    """One normalized measurement from a collector (DCGM, RDMA counters, host, disk)."""

    schema_v: Literal[1] = 1
    ts_utc_ns: UtcNs
    node: str = Field(min_length=1)
    metric: str = Field(min_length=1, description="name as discovered from the source")
    entity: EntityKind
    entity_id: str = Field(min_length=1)
    value: float
    unit: str
    provenance: Provenance
