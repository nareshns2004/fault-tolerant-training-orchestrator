# Evaluation — goodput

Every number that leaves this repo is produced by the process in this document.

## 1. Metric definitions (canonical)

All times are derived from the event log (state-machine transitions + ledger), never from
ad-hoc timers.

- **t_fault**: `FaultInjection.t_start_utc_ns` (for real harvested faults: earliest
  evidence event).

### 1.1 System-agnostic metrics (used for every comparison against a baseline)

These need nothing from goodput's own state machine, so they apply equally to goodput,
B0, B0-tuned, B1 and B2 (resolves OQ-3).

- **TTD** (time to detect) = t(first *detection event*) − t_fault. A detection event is the
  first externally observable signal that the system has noticed the fault: for goodput,
  its first `Verdict` with the correct class; for baselines, the first of: ProcessGroupNCCL
  watchdog/timeout or async-error log line, torchrun observing a worker exit, or a NCCL
  error surfaced to the training script. Parsed from logs by `bench`, never by modifying
  the baseline.
- **TTR** (time to recover, end to end) = t(first productive step completed after the
  fault) − t_fault. Includes detection, so no system can hide slow detection behind fast
  recovery.
- **Recovery phases**: TTR is always reported **decomposed**: detect · abort/drain ·
  reschedule/placement · process start · CUDA init · NCCL communicator init · checkpoint
  load (by tier) · compile/warmup · first step. For baselines the phases come from
  timestamps in the training script plus parsed torchrun/NCCL logs (OQ-10).

Headline targets #1, #2, #7, #8 are stated in TTD/TTR.

### 1.2 goodput-internal diagnostics

- **MTTD (internal)** = t(SUSPECT→DECIDED with correct class) − t_fault. A detection with
  the wrong class does not count as detected; it is recorded separately as a
  misclassification.
- **MTTR (internal)** = t(back to RUNNING, first productive step completed) − t(DECIDED).
  Useful for tuning goodput itself; never used to compare against a baseline.

### 1.3 Other metrics

- **Lost work** = (step at fault − step of restored checkpoint) × median step time.
- **Goodput** = Σ productive step time / wall time over the run. Productive = steps whose
  results survive into the final model (steps rolled back do not count). Also report
  ETTR in the sense of the Meta reliability paper for comparability, and note any
  definitional differences.
- **Attribution accuracy** = fraction of trials where `Verdict.culprit` matches the ledger
  target at the stated granularity (rank; and component: gpu/nic/port/node/storage).
- **Classification**: per-class precision/recall/F1, macro-F1, full confusion matrix.
- **False-positive rate**: cordons or restarts issued during fault-free windows, per 24 h.
- **Steady-state overhead** = (step_time_with_goodput − step_time_without) / without.
- **Checkpoint cost C**: blocking stall per checkpoint, per tier; plus background bandwidth.

## 2. Baselines

- **B0** — stock: `torchrun` with max restarts, default ProcessGroupNCCL timeout and async
  error handling as shipped by the installed PyTorch version (record the values), synchronous
  DCP to shared storage every K steps.
- **B0-tuned** — B0 with `NCCL_IB_TIMEOUT`, `NCCL_IB_RETRY_CNT` and the ProcessGroupNCCL
  timeout tuned as aggressively as the workload tolerates without spurious failures in a
  fault-free run (record the chosen values and how they were chosen). Detection targets are
  stated against the *stronger* of B0 and B0-tuned, so the comparison is never against a
  strawman (resolves OQ-4).
- **B1** — B0 + async DCP save at the same interval.
- **B2 (Should)** — NVRx components (straggler detection / in-process restart / local
  checkpointing / flight-recorder attribution) where applicable, configured per their docs.
  For culprit-rank accuracy (#3) NVRx's flight-recorder attribution is the comparison,
  not only "first rank to report" (`docs/prior_art.md`). If goodput loses to B2 on some
  axis, publish it and explain.
- K for baselines is chosen via Young/Daly (§4.2) using measured C and the experiment's
  MTBF, so baselines are not strawmen.

## 3. Workloads

- Dev: small decoder (nanoGPT-class) single node, CPU-gloo for logic tests.
- Primary: torchtitan Llama-architecture model (≈1B for iteration, ≈8B for headline results)
  with FSDP2, and TP within node when GPUs per node allow. Fixed seed, fixed data order,
  synthetic or public dataset (no private data).
- Record model size, parallelism layout, global batch, sequence length, step time, and MFU
  so results are interpretable.

## 4. Experimental protocol

- **Detection/attribution trials:** ≥ 20 trials per fault class per configuration;
  injection step and target randomized from a seeded RNG; report p50/p90 and max with 95%
  CIs (bootstrap). Report failures and misattributions individually, not just aggregates.
- **Goodput runs:** ≥ 12 h per system variant; faults drawn from a Poisson process with a
  compressed MTBF (state the value and the class mix); same fault schedule (same seed)
  replayed for goodput and each baseline. Include one fault-free run per variant for
  false-positive and overhead measurement.
- **Overhead:** A/B with goodput disabled vs enabled, same seed, ≥ 500 steps after warmup,
  interleaved runs to control for thermal/drift; report mean ± CI.
- **Correctness after recovery:**
  - Sample ledger: no sample id seen twice or skipped relative to the reference order.
  - Loss trajectory: compare against an uninterrupted reference run; state the tolerance
    and why (bitwise equality only if deterministic mode is enabled and resharding didn't
    occur; elastic shrink changes numerics — explain).
  - Optimizer and LR-scheduler state restored (check step counters and a state checksum).
  - RNG state restored (dropout masks reproducible where deterministic mode is on).
- **Elastic shrink:** global batch preserved via gradient accumulation; document effect on
  throughput and on numerics.

### 4.1 Sample-size rules (resolves OQ-5 to OQ-8)

A target is only "met" if the stated sample size can actually demonstrate it.

| Claim | Minimum evidence | Why |
|---|---|---|
| A p99 latency | ≥ 100 trials; with fewer, report p90 and max instead | With 20 trials the p99 is just the maximum |
| Accuracy ≥ 95% | ≥ 60 trials per class with zero misses, or report the 95% lower confidence bound (Wilson / Clopper-Pearson) actually achieved | Rule of three: 20/20 only bounds accuracy at ≈ 85% |
| False-positive rate ≤ 1 per 24 h | ≥ 72 h fault-free with zero events; otherwise report the achieved upper bound (≈ 3 / hours × 24) | Zero events in 12 h only bounds the rate at ≈ 6 per 24 h |
| Goodput gain over a baseline | Report across an MTBF sweep, with the anchor MTBF derived from published per-GPU interruption rates scaled to the tested cluster size (source cited) | A single chosen MTBF can buy any gain |

### 4.2 Checkpoint interval

K for every system is τ ≈ √(2·C·MTBF) (Young/Daly) with measured C. *Worked example,
calculation only:* C = 30 s and a compressed MTBF of 1 h give τ ≈ 465 s (≈ 8 min). For the
overhead metric (#9), state the tier-0 snapshot frequency explicitly (OQ-14).

## 5. Reporting standard

- Every result lives in `bench/results/<run_id>/`: config, env manifest (GPU model, driver,
  CUDA, NCCL, PyTorch, torchtitan commit, NIC model + firmware, kernel, OFED/rdma-core,
  relevant NCCL/torch env vars, topology.json hash), raw event log, telemetry extracts,
  and the generated report. Summaries (not raw bulk) are committed.
- Reports are generated by script (`make report RUN=…`); no hand-edited numbers.
- Plots: MTTD CDF per class; MTTR stacked-phase bars per path; goodput timeline with fault
  markers; confusion matrix; overhead distribution; simulator projection curves.
- Any claim in README/blog links to a run id.

## 6. Simulator validation

The simulator is calibrated with measured phase distributions and checkpoint costs, then:
(a) reproduces measured goodput at the tested scale within a stated error; only then
(b) projects to larger scales using literature failure rates, labeled as projection, with a
sensitivity analysis on MTBF and checkpoint interval.
