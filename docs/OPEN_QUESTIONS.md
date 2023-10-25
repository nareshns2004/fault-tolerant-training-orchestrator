# Open questions

These are contradictions, ambiguities and weak targets found while reviewing the docs
(2026-09-28). Each needs a decision, recorded in an ADR where it changes a schema,
metric or target. Delete an entry once it is resolved and link to where it was resolved.

## Blockers (resolve before the dependent code is written)

**OQ-1 · Target hardware is undefined.** M1 needs torchtitan 8B on ≥ 2 nodes with an
RDMA fabric, and M5 needs spare nodes. `docs/ENVIRONMENT.md` is empty. The cluster size,
NIC/rail layout, switch access and publication clearance decide what M1–M5 can
demonstrate.

**OQ-2 · FAULT_MATRIX labels contradict CLAUDE.md rule 4.** F01, F08, F09, F10, F13,
F14, F16 and F18 are labelled **R**, but each one is triggered on purpose, which rule 4
defines as **induced**. It also needs deciding what a label means on a *telemetry sample*.
The proposal in `goodput.schemas.Provenance` is that the label describes the value's
origin, so a genuinely measured counter is `real`, and the fault's own label lives on
`FaultInjection`. This blocks the M2 ledger.

**OQ-3 · MTTD and MTTR cannot be computed for the baselines.** EVALUATION §1 defines both
from goodput's own state transitions (SUSPECT→DECIDED, DECIDED→RUNNING), which B0 and B1
don't have. Yet targets #1, #2, #7 and #8 compare against B0. We need definitions that
apply to any system (for example t_fault → first detection event, and
t_fault → first productive step). We also need an end-to-end time-to-recover, because
MTTR measured from DECIDED hides detection time. This blocks `bench/metrics.py`.

**OQ-4 · Risk of a strawman detection baseline.** ProcessGroupNCCL's default timeout is
long (verify the value for the pinned PyTorch version). For link-down, NCCL's own error
path is bounded by the IB local-ack timeout × retry count (FAULT_MATRIX gotchas). With
some plausible default settings, that bound is already near the 30 s target for metric #1.
Proposal: add a B0 variant with tuned timeouts, and state targets as improvements over
the strongest baseline.

## Statistics

**OQ-5 · p99 from 20 trials is just the maximum value** (metrics #1 and #2). Either
require more trials or report p90 and max.

**OQ-6 · "≥ 95% accuracy over ≥ 20 trials" can't be shown.** With 20 successes out of
20, the rule of three puts the 95% lower confidence bound at about 85%. Showing ≥ 95%
needs roughly 60 or more trials per class. The same applies to metric #5.

**OQ-7 · The false-positive target can't be measured with one 12 h fault-free run.**
Zero events in 12 h only bounds the rate at about 6 per 24 h (rule of three). Either run
longer fault-free, or state the bound you actually achieve.

**OQ-8 · The goodput gain depends on the chosen MTBF.** The +10-point target (#10) can be
reached by picking the MTBF. Document where the MTBF comes from (for example, literature
per-GPU failure rates scaled to a stated cluster size) and report a sweep across MTBF
values, not one point.

## Scope and feasibility

**OQ-9 · M1 is overloaded.** Proposal: split it into M1a (scaffold, CPU harness,
prior-art gate) and M1b (baselines on the cluster).

**OQ-10 · "Instrument phases for the baseline" conflicts with "B0 is stock."** We need a
way to instrument B0 without modifying it, such as timestamps in the training script plus
parsed torchrun and NCCL logs. This is part of the `[OWNER-CORE]` instrumentation design.

**OQ-11 · M1 link-down trials come before faultlab's revert and watchdog (M2).** Either
build a minimal revert harness in M1, or run only SIGKILL trials in M1.

**OQ-12 · The in-process single-rank restart is the riskiest item and is scheduled
last.** It means aborting the communicator in the surviving processes and rebuilding
FSDP2's mesh. Run a feasibility spike in M1 or M2, and write down which fault classes it
is and isn't safe for.

**OQ-13 · "Transient fault" (metric #7) is not mapped to any fault ID.** Every metric
should list its fault IDs.

**OQ-14 · The overhead target (#9) doesn't say how often tier 0 checkpoints are taken.**
The overhead depends almost entirely on that frequency.

**OQ-15 · Node replacement (#8) needs a spare node.** At tens of GPUs a spare may not
exist, and then the only option is elastic shrink, which is Should-tier.

**OQ-16 · The back-of-envelope in the brief (§4) only covers the peer tier.** Eight ranks
share a node's NICs unless the node is rail-optimized. The baselines restore from shared
storage, whose bandwidth, not the NIC's, sets their load time.

## Other

**OQ-17 · Dataset size.** About 20 trials across roughly 12 classes gives a few hundred
incidents, a thin base for fine-tuning ModernBERT. Splitting by node on 2–4 nodes also
leaves a very small test set.

**OQ-18 · Decisions still open with no ADR:** gRPC vs HTTP/JSON (ADR-0002), c10d store vs
etcd, and the job-lease mechanism (ARCHITECTURE §6).

**OQ-19 · Public-release hygiene.** `CLAUDE.md` and the risks table in PROJECT_BRIEF
mention an employer POC. Decide what is published before the first public push.
