# Open questions

These are contradictions, ambiguities and weak targets found while reviewing the docs
(2026-09-28; updated 2026-11-11). Each needs a decision, recorded in an ADR where it changes a schema,
metric or target. Delete an entry once it is resolved and link to where it was resolved.

## Blockers (resolve before the dependent code is written)

**OQ-1 · Target hardware is undefined.** M1b needs torchtitan 8B on ≥ 2 nodes with an
RDMA fabric, and M5 needs spare nodes. `docs/ENVIRONMENT.md` is empty. The cluster size,
NIC/rail layout, switch access and publication clearance decide what M1–M5 can
demonstrate.

## Scope and feasibility

**OQ-10 · "Instrument phases for the baseline" conflicts with "B0 is stock."** We need a
way to instrument B0 without modifying it, such as timestamps in the training script plus
parsed torchrun and NCCL logs. This is part of the `[OWNER-CORE]` instrumentation design.

**OQ-11 · M1b link-down trials come before faultlab's revert and watchdog (M2).** Either
build a minimal revert harness in M1b, or run only SIGKILL trials in M1b.

**OQ-13 · "Transient fault" (metric #7) is not mapped to any fault ID.** Every metric
should list its fault IDs.

**OQ-14 · The overhead target (#9) doesn't say how often tier 0 checkpoints are taken.**
The overhead depends almost entirely on that frequency.

**OQ-15 · Node replacement (#8) needs a spare node.** At tens of GPUs a spare may not
exist, and then the only option is elastic shrink, which is Should-tier.

## Other

**OQ-17 · Dataset size.** About 20 trials across roughly 12 classes gives a few hundred
incidents, a thin base for fine-tuning the RCA model (ADR-0005), even with the larger
per-class trial counts in EVALUATION §4.1. Splitting by node on 2–4 nodes also
leaves a very small test set.

**OQ-18 · Decisions still open with no ADR:** gRPC vs HTTP/JSON (ADR-0002), c10d store vs
etcd, and the job-lease mechanism (ARCHITECTURE §6).

**OQ-20 · One public name.** The repository is `fault-tolerant-training-orchestrator`,
the package and CLI are `goodput`, and the Hugging Face artifacts are `nccl-incident-rca` /
`qwen3-nccl-rca-lora`. "Orchestrator" also undersells the contribution, which is
attribution rather than orchestration. Decide the public name before the first release;
renaming the package after a PyPI release is expensive. The distribution name `goodput` is
already taken on PyPI (checked 2026-11-11), so at minimum the distribution needs another
name (the import package can stay `goodput`).

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
| OQ-19 · Public-release hygiene | Personal and employer references removed from tracked files; local notes live in `.local/` (gitignored) | CLAUDE.md, PROJECT_BRIEF §10 |
