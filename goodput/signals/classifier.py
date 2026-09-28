"""Classifier interface. v1 = deterministic rules; v2 = Hugging Face model, same interface.

Both versions are evaluated on the same held-out incidents (PROJECT_BRIEF.md §7: no ML in
the core path until rules-based attribution is measured).
"""

from __future__ import annotations

from typing import Protocol

from goodput.schemas import Incident, Verdict


class Classifier(Protocol):
    version: str

    def classify(self, incident: Incident) -> Verdict:
        """Return a verdict with evidence. Abstain with ``FaultClass.UNKNOWN``, never guess."""
        ...
