# Project Brief — goodput

## 1. One-line pitch

When a 1,000-GPU training job hangs, every rank reports a timeout, but only one component is
actually broken. goodput finds that component in seconds instead of minutes, recovers without
restarting the healthy 99%, and proves the goodput gain with reproducible measurements.

## 2. The problem

Large training runs are interrupted constantly, and most interruptions are infrastructure,
not ML, failures. Reference points to anchor the problem (verify each against the primary
source during the M1 prior-art review and cite section numbers in `docs/prior_art.md`):

- Meta, *The Llama 3 Herd of Models* (2024), infrastructure/reliability section: over a
  ~54-day window of 405B pretraining on ~16K H100s, a few hundred unexpected interruptions,
  the large majority attributed to confirmed or suspected hardware issues, with GPU and HBM
  faults the largest categories; effective training time reported above 90%.
- ByteDance, *MegaScale* (NSDI 2024): 10K+ GPU training; a dedicated robust-training
  framework (heartbeats, diagnostic self-checks, fast checkpoint/recovery) was necessary to
  keep effective training time high.
- Meta, *Revisiting Reliability in Large-Scale ML Research Clusters* (2024): defines
  Effective Training Time Ratio (ETTR) and shows how failure rates scale with job size.
- Checkpointing literature: CheckFreq (FAST '21), Check-N-Run (NSDI '22), GEMINI in-memory
  checkpointing (SOSP '23); Young (1974) / Daly (2006) optimal checkpoint interval.

Why it is hard, in one paragraph: **symptoms are global, causes are local.** A single bad
GPU, NIC, cable, or switch port stalls a collective, and every rank in that communicator sees
the same timeout. Default detection is a watchdog timeout measured in minutes. Default
recovery restarts the whole job from the last durable checkpoint, paying process restart,
CUDA context creation, NCCL communicator init, checkpoint load, and compile warmup across all
ranks — plus the work lost since the last checkpoint. Wrong attribution is expensive in both
directions: missing the culprit means the job re-crashes on the same bad hardware; cordoning a
healthy node burns capacity.

## 3. Positioning — what exists and where the gap is

This project must have a crisp answer to "why not just use X?". Build on these, don't compete
with them:

| Existing tool | What it does well | What this project adds |
|---|---|---|
| `torchrun` / TorchElastic | Rendezvous, restart on process failure, elastic membership | Knows *why* it failed and *where*; avoids restarting onto bad hardware |
| PyTorch ProcessGroupNCCL watchdog + flight recorder | Detects collective timeouts; dumps per-rank collective history | Cross-rank analysis of those dumps to name the culprit; joins with hardware/fabric telemetry |
| PyTorch DCP (incl. async save) | Sharded, reshardable checkpoints | Tiered, failure-domain-aware placement; restore-path selection per fault class |
| torchft | Per-step fault tolerance via replica groups | Attribution + fabric-layer signals; complementary, possibly integrable |
| NVIDIA Resiliency Extension (NVRx) | Straggler detection, in-process restart, local checkpointing | Fabric-layer (RoCE/IB) attribution and topology-aware policy; evaluate NVRx as a component or baseline in M1 |
| DCGM / dcgm-exporter | GPU health fields, XIDs, diagnostics | Correlation of GPU events with training symptoms and rank mapping |
| Slurm / Kubernetes (JobSet, Kueue) | Scheduling, node lifecycle | goodput is not a scheduler; it drives cordon/replace decisions through them |

**Claimed gap (to be validated in M1, not assumed):** open-source tooling covers
compute-side detection and restart reasonably well, but cross-layer attribution — joining
PyTorch/NCCL symptoms with GPU health *and* RDMA fabric state (link state, retransmit/
timeout counters, ECN/CNP, PFC pause) through an explicit topology model — is weakly covered.
That fabric layer is Naresh's differentiator. If the M1 review shows the gap is already
closed, re-scope before M2; do not build a me-too.

## 4. Thesis

    goodput = productive_step_time / wall_time
    loss per fault ≈ MTTD + MTTR + lost_work + (false_positive_rate × capacity_cost)

The lever this project pulls is **fast, correct attribution** (right rank, right component,
right failure domain). Correct attribution enables minimal-blast-radius recovery: in-process
communicator re-init for transient faults, targeted node replacement for hard faults, and
restore from a peer's in-memory checkpoint that was deliberately placed in a different
failure domain.

Hypothesis to test explicitly (it shapes M5): at the scale available here (tens of GPUs),
MTTR is dominated by re-initialization (process restart, CUDA context, NCCL init, compile
warmup), not checkpoint I/O. Back-of-envelope: an 8B model with bf16 weights, fp32 master
weights and Adam state is ~16 bytes/param ≈ 128 GB total; sharded over 16 GPUs that is ~8 GB
per rank, which a 400 Gb/s NIC moves in well under a second. If measurements confirm the
hypothesis, in-process recovery matters more than faster storage. If they refute it, say so
in the write-up — a refuted hypothesis with data is a stronger interview story than an
unexamined one.

## 5. Objectives

- **O1 Fault realism.** A reproducible fault-injection harness covering process, GPU,
  host, NIC/fabric, storage, and control-plane faults, each with a ground-truth ledger.
- **O2 Fast detection.** Detect hard faults and hangs far faster than default watchdog
  timeouts, with no meaningful steady-state overhead.
- **O3 Correct attribution.** Name the culprit rank and physical component (GPU / NIC /
  link / node / storage) with published precision/recall per fault class.
- **O4 Minimal-blast-radius recovery.** Topology-aware policy choosing among in-process
  re-init, rank/node replacement, elastic shrink, and rollback — per fault class.
- **O5 Provable goodput gain.** Goodput under a controlled fault schedule vs stock
  baselines, with MTTR decomposed into phases and correctness of recovered training verified.
- **O6 Reusable signal.** A versioned, labeled dataset of fault signatures and telemetry
  that directly trains the downstream Hugging Face models.

## 6. Measurable outcomes

Targets are hypotheses to be confirmed or revised with data in M1 once baselines exist.
Metric definitions live in `docs/EVALUATION.md`; do not redefine them elsewhere.

| # | Metric | Target (initial) | Compared against |
|---|---|---|---|
| 1 | MTTD, hard faults (rank crash, node loss, link down) | p99 ≤ 30 s | Baseline B0 watchdog/elastic detection |
| 2 | MTTD, stuck-rank hang | p99 ≤ 60 s | B0 (PG timeout) |
| 3 | Culprit-rank attribution accuracy, hangs/desync | ≥ 95% over ≥ 20 trials per class | "First rank to report" heuristic |
| 4 | Fault-class classification | macro-F1 ≥ 0.90 on fault matrix; confusion matrix published | Per-class majority baseline |
| 5 | Straggler detection (≥ 20% slowdown on one GPU/host) | detected ≤ 50 steps, correct rank ≥ 95% | NVRx straggler detector if adopted as baseline |
| 6 | False-positive cordons | ≤ 1 per 24 h fault-free run | — |
| 7 | MTTR (post-detection), transient fault, in-process path | ≤ 60 s, phase-decomposed | B0 full restart |
| 8 | MTTR, node replacement with peer in-memory restore | ≤ 3 min, phase-decomposed | B1 restore from durable storage |
| 9 | Steady-state overhead (monitoring + tiered ckpt) | ≤ 2% step time, with CI | Same config, goodput disabled |
| 10 | Goodput under fault schedule (≥ 12 h, compressed MTBF) | ≥ 90% and ≥ +10 pts over B0 | B0, B1 |
| 11 | Recovery correctness | zero duplicated/skipped samples; loss trajectory within stated tolerance of an uninterrupted run | Uninterrupted reference run |
| 12 | Scale projection | Simulator calibrated on measured phases; projections at 1K/4K/16K GPUs sanity-checked against published ETTR | Literature values (labeled) |

## 7. Non-goals

- Not a scheduler, not a training framework, not a new checkpoint format.
- Not a replacement for torchrun/NVRx/torchft; integrate where they fit.
- No hardware-damaging fault injection. No claims about fault rates at scales not run.
- No ML-based classifier in the core path until rules-based attribution is measured
  (the ML model is the Hugging Face project's job, plugged in behind an interface).

## 8. Scope tiers

- **Must:** faultlab for process/hang/desync/straggler/NIC-link/storage faults; flight-
  recorder-based culprit attribution; DCGM + RDMA-counter + kernel-log collectors; topology
  model; rules classifier; policy engine with in-process re-init and node replacement;
  tiered checkpoint (host memory + peer replica + durable async); full evaluation vs B0/B1;
  dataset export; write-up.
- **Should:** elastic shrink preserving global batch; Grafana dashboards; goodput simulator;
  NVRx as baseline or component; congestion/PFC fault class.
- **Stretch:** silent data corruption (SDC) detection via cross-replica checksums / grad-norm
  anomaly; raw-verbs checkpoint replicator shared with the inference repo's transport;
  HA controller.

## 9. Relationship to the rest of the portfolio

- **Hugging Face 1 (ModernBERT incident classifier):** trained on this repo's labeled
  signature dataset (M3/M4 export). Plugs back in behind `signals.Classifier`.
- **Hugging Face 2 (Qwen3 + LoRA RCA reasoner):** trained on incident bundles (events +
  verdict + evidence) this repo emits; produces narrative root-cause reports.
- **Inference repo:** complementary "efficiency at scale" story; shares the fault-injection
  mindset (request success under fault) and possibly the RDMA transport library (Stretch).

## 10. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Real GPU faults (XIDs, ECC) cannot be induced safely | Induced mechanisms + clearly labeled synthetic DCGM injection; harvest any real faults that occur; never overclaim |
| Scale too small to show fabric effects | Engineer contention (competing RDMA traffic), link flaps, PFC; calibrated simulator for projections |
| Gap already closed by NVRx/torchft | M1 prior-art gate; re-scope toward fabric attribution if needed |
| Employer IP overlap with internal POC | Clean-room rule; written clearance before public push; separate hardware provenance |
| Claude Code writes code Naresh can't defend | `[OWNER-CORE]` boundaries + `/drill` after each component |
| Polish crowding out building | Write-up is M6 only; README stays a stub until then |

## 11. Public deliverables (M6)

README with a 90-second "why this matters" + results table; architecture doc; results report
with every number traceable to a run id; blog post; short demo recording (inject → detect →
attribute → recover, with a live goodput counter); published dataset card.
