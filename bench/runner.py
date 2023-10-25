"""Experiment runner: ``make bench SCENARIO=...`` -> ``bench/results/<run_id>/`` (M1)."""

from __future__ import annotations

from pathlib import Path


def run(scenario: Path, results_root: Path = Path("bench/results")) -> Path:
    """Run one experiment and return its results directory."""
    raise NotImplementedError("M1: experiment runner")
