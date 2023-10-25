"""faultlab: fault injection and the ground-truth ledger.

Deliberately a separate package from ``goodput`` (ADR-0004):
* it is the *adversary*: the system under test must not be able to read the ledger, or
  attribution results are contaminated by ground truth;
* it runs with different privileges (``ip link``, ``nvidia-smi -lgc``) than the detector.

``faultlab`` may import ``goodput.schemas`` and nothing else from ``goodput``.
"""
