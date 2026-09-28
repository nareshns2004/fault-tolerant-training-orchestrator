"""goodput: cross-layer fault attribution and minimal-blast-radius recovery for LLM training.

This package is the *system under test*. It must never import ``faultlab`` (the fault
injector and ground-truth ledger) or ``bench`` (the evaluator); see ADR-0004 and
``tests/unit/test_import_boundaries.py``.
"""

__version__ = "0.0.1"
