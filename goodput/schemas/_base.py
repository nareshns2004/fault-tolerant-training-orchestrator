"""Shared base for every cross-component message.

Conventions (CLAUDE.md, ARCHITECTURE.md §4):

* Every model carries ``schema_v``. A breaking change bumps it; readers reject versions
  they do not understand rather than guessing.
* Models are immutable and reject unknown fields, so a producer/consumer skew fails
  loudly instead of silently dropping data.
* Two clocks, never mixed:
  ``*_utc_ns``  — wall-clock UTC epoch nanoseconds, used to *correlate across hosts*.
                  Only as good as clock sync (chrony/PTP); see docs/ENVIRONMENT.md.
  ``*_mono_ns`` — CLOCK_MONOTONIC nanoseconds, used for *durations on one host only*.
                  Meaningless across hosts or across reboots.
"""

from __future__ import annotations

import time
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

UtcNs = Annotated[int, Field(ge=0, description="UTC epoch nanoseconds (cross-host correlation)")]
MonoNs = Annotated[int, Field(ge=0, description="CLOCK_MONOTONIC ns (same-host durations only)")]


class SchemaModel(BaseModel):
    """Frozen, strict base model for all goodput schemas."""

    model_config = ConfigDict(frozen=True, extra="forbid", str_strip_whitespace=True)


def now_utc_ns() -> int:
    """Current wall-clock time as UTC epoch nanoseconds."""
    return time.time_ns()


def now_mono_ns() -> int:
    """Current CLOCK_MONOTONIC time in nanoseconds."""
    return time.monotonic_ns()
