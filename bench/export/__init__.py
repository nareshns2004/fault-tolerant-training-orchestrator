"""Incident dataset export (M3+, ADR-0005).

Lives in ``bench`` because every record joins system output (``Incident``, rules
``Verdict``) with ground truth (the faultlab ledger), and ADR-0004 allows that join only in
``bench``. One JSON line per incident: the contract is ``bench.export.record.IncidentRecord``,
published as ``docs/schemas/incident.schema.json`` (``make schemas``). The builder that reads
``bench/results/<run_id>/`` arrives with M3.
Splits group by run and hold out topologies and harvested real faults; never split by
random record.
"""
