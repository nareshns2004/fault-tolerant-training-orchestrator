# Open questions

These are contradictions, ambiguities and weak targets found while reviewing the docs
(2026-09-28; updated 2026-11-13). Each needs a decision, recorded in an ADR where it changes a schema,
metric or target. Delete an entry once it is resolved and link to where it was resolved.

## Blockers (resolve before the dependent code is written)

**OQ-1 · Target hardware is undefined.** M1b needs torchtitan 8B on ≥ 2 nodes with an
RDMA fabric, and M5 needs spare nodes. `docs/ENVIRONMENT.md` is empty. The cluster size,
NIC/rail layout, switch access and publication clearance decide what M1–M5 can
demonstrate.

## Resolved

| OQ | Resolution | Where |
|---|---|---|
| OQ-2 · R/I/S labels | R only for harvested faults; scheduled faults are I or S; telemetry label describes the value | [ADR-0006](adr/0006-provenance-labels.md), FAULT_MATRIX |
| OQ-3 · Baseline-applicable MTTD/MTTR | System-agnostic TTD and end-to-end TTR; internal MTTD/MTTR kept as diagnostics | EVALUATION §1.1 |
| OQ-4 · Strawman detection baseline | B0-tuned added; detection targets stated against the stronger of B0 and B0-tuned | EVALUATION §2 |
| OQ-5 to OQ-8 · Statistics | Sample-size rules; targets restated as p90 + max, lower confidence bounds, achieved FP bound, MTBF sweep | EVALUATION §4.1, PROJECT_BRIEF §6 |
| OQ-9 · M1 overloaded | Split into M1a (CPU, prior art) and M1b (cluster baselines) | MILESTONES |
| OQ-12 · In-process restart scheduled last | Feasibility spike moved to M2 | MILESTONES |
| OQ-16 · Back-of-envelope covers only the peer tier | NIC sharing and shared-storage caveats added | PROJECT_BRIEF §4 |
| OQ-10, 11, 13, 14, 15, 17, 18, 20 | Baseline instrumentation, M1b fault scope, metric fault IDs, tier-0 interval, no-spare fallback, dataset size and downstream model, control-plane transport and lease, public name | [ADR-0007](adr/0007-open-questions-resolved.md) |
| OQ-19 · Public-release hygiene | Personal and employer references removed from tracked files; local notes live in `.local/` (gitignored) | CLAUDE.md, PROJECT_BRIEF §10 |
