"""Incident dataset export (M3+, ADR-0005).

Lives in ``bench`` because every record joins system output (``Incident``, rules
``Verdict``) with ground truth (the faultlab ledger), and ADR-0004 allows that join only in
``bench``. One JSON line per incident, validated against ``docs/schemas/incident.schema.json``.
Splits group by run and hold out topologies and harvested real faults; never split by
random record.
"""
