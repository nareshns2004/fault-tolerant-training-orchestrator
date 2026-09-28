"""Correlator: turns a trigger into an ``Incident`` by windowing and topology join."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Protocol

from goodput.schemas import Event, Incident, Topology


class Correlator(Protocol):
    def build_incident(
        self, trigger: Event, events: Iterable[Event], topology: Topology
    ) -> Incident:
        """Select events within the window around ``trigger`` and slice ``topology`` to
        the affected communicator. Cost must scale with the communicator, not the cluster.
        """
        ...
