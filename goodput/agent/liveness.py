"""Rank liveness classification. Distinguishing these is the whole point of the agent."""

from __future__ import annotations

from enum import StrEnum


class Liveness(StrEnum):
    ALIVE = "alive"  # process up, heartbeat fresh, progress advancing at normal rate
    SLOW = "slow"  # progress advancing, but step time is an outlier (straggler candidate)
    HUNG = "hung"  # process up, heartbeat fresh, progress stalled
    DEAD = "dead"  # process exited or heartbeat lost
