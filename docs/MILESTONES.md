# Milestones — goodput

A milestone is done only when every exit criterion is met with evidence (run ids, test
names, docs). `[OWNER-CORE]` = a maintainer writes the implementation; other contributors
(human or AI) design interfaces, write tests/fixtures, and review.

The order is deliberate: answer the two biggest unknowns first (*does the gap exist?* in
M1a, *can in-process recovery work at all?* in M2), then inject faults (M2), prove
attribution (M3, M4), and only then build recovery (M5). M1 is split into a CPU-only part
and a cluster part (resolves OQ-9); the in-process restart spike moves to M2 (resolves
OQ-12).

---

## M1a — Scaffold, CPU harness, prior-art gate (no cluster needed)

**Goal:** a validated reason to exist, and a repo a stranger can build and test.

Deliverables
- Repo scaffold, `make setup/check`, CI running CPU tests. *(done)*
- `docs/prior_art.md`: MegaScale, Llama 3 reliability section, Meta ETTR paper, GEMINI,
  CheckFreq, torchft, NVRx (including its experimental flight-recorder attribution
  module), PyTorch flight recorder — each with: mechanism, what it covers, what it leaves
  open, what we reuse. Ends with a go/re-scope decision on the claimed gap.
- `docs/ENVIRONMENT.md` manual section filled: target hardware, NIC/rail layout, switch
  access, clearance (OQ-1).
- Metric definitions usable for baselines (TTD/TTR, EVALUATION §1.1) and the B0-tuned
  baseline defined. *(done)*

Exit criteria
- Prior-art gate decision written, with the claimed gap stated against NVRx attribution.
- ADR-0003 accepted or revised in light of the prior-art review.
- OQ-1 resolved.

`[OWNER-CORE]`: the prior-art gap analysis.

---

## M1b — Workload harness, baselines, topology (on the cluster)

**Goal:** a measured, reproducible "before" picture.

Deliverables
- `make env-manifest` and `make topo` producing `docs/ENVIRONMENT.md` generated section and
  `artifacts/topology.json` (rank → GPU → NUMA → NIC/port → rail → switch where discoverable).
- torchtitan workload running at 1B (iteration) and 8B (headline) with FSDP2 on ≥ 2 nodes;
  step time and MFU recorded.
- Baselines B0, B0-tuned and B1 implemented; SIGKILL trials measured with TTR phase
  decomposition, instrumenting the baseline without modifying it (OQ-10). Link-down trials
  only once a minimal revert harness exists (OQ-11); otherwise they move to M2.
- Revisit targets in PROJECT_BRIEF §6 with baseline data; record changes in an ADR.

Exit criteria
- A stranger could reproduce the B0 run from docs alone.
- Baseline TTR decomposition exists for ≥ 2 fault types with ≥ 5 trials each.
- ADR-0001/0002 accepted or revised.

`[OWNER-CORE]`: the TTR phase instrumentation design.

---

## M2 — faultlab: injection harness + ground-truth ledger

**Goal:** every Must fault in FAULT_MATRIX is injectable on demand, reproducibly, safely.

Deliverables
- Scenario YAML schema + runner; target selectors resolved via topology.json.
- LD_PRELOAD interposer (C) for NCCL/CUDA: hang at (rank, step, op), return error,
  mismatch op/size. Unit-tested with a fake NCCL shim on CPU where possible.
- Mechanisms for F01–F05, F08, F09, F11, F12(S), F14–F16, F18.
- Ledger writer; registered revert per injection; watchdog auto-revert; startup sweep that
  reverts stale injections.
- Safety: host allowlist enforced; destructive mechanisms require an explicit flag.
- **In-process restart feasibility spike** (moved up from M5, OQ-12): kill or hang one rank
  of a small FSDP2 job, abort communicators in the survivors, rebuild the mesh, and resume.
  Record per fault class where it works, where it does not (poisoned communicator, sticky
  CUDA error, network partition), and the phase timings. Throwaway code is fine; the
  written result is the deliverable.

Exit criteria
- Each Must fault injected ≥ 20 times with 100% ledger completeness and 100% verified revert.
- Poisson fault scheduler produces a replayable schedule from a seed.
- Feasibility spike written up; M5 scope confirmed or re-planned from its result.

`[OWNER-CORE]`: the NCCL interposer hang/mismatch logic; revert/watchdog design; the
in-process restart spike.

---

## M3 — NCCL/PyTorch signature capture + culprit attribution

**Goal:** name the culprit rank for hangs, crashes, desyncs, and transport errors — fast.

Deliverables
- Flight recorder enabled and dumps collected from all ranks on trigger and on demand.
- Cross-rank analyzer: aligns per-rank collective sequences, identifies ranks that never
  entered / never completed / diverged; combines with progress beacons. Per ADR-0003 and
  the prior-art gate, either wraps NVRx's flight-recorder attribution or is benchmarked
  against it.
- Rules classifier v1 for F01–F04, F11; `Verdict` with evidence references.
- Signature catalogue (`docs/signatures.md`): per class, the observable fingerprint and why.
- Dataset export v0 (ADR-0005), with provenance labels and leakage-safe splits.

Exit criteria
- Metrics #2, #3 in PROJECT_BRIEF met (at EVALUATION §4.1 sample sizes) or the gap
  explained with data.
- Confusion matrix for F01–F04, F11 over ≥ 20 trials each.
- CPU tests replay recorded flight-recorder fixtures deterministically.

`[OWNER-CORE]`: the cross-rank sequence analyzer and the rules for hang vs desync vs crash.

---

## M4 — Telemetry pipeline + cross-layer correlation

**Goal:** attribute to the physical component (GPU / NIC / port / link / node / storage).

Deliverables
- Agent collectors: DCGM, RDMA port counters + hw_counters, ethtool PFC stats, kernel log
  (XID/mlx5/AER), host metrics, checkpoint-volume latency.
- Counter discovery (no hardcoded counter names); rate computation and change-point
  detection per counter.
- Correlator joining events via topology; classifier extended to F05–F10, F12–F14.
- Straggler detector (per-rank step-time decomposition, robust statistics).
- Prometheus + Grafana dashboards: per-rank progress, per-GPU health, per-port fabric view.

Exit criteria
- Metrics #1, #4, #5, #6 measured; #9 overhead ≤ target with CI.
- Fabric faults (F08–F10) attributed to the correct port/rail.

`[OWNER-CORE]`: RDMA counter semantics and anomaly rules (the project's core contribution).

---

## M5 — Topology-aware recovery + tiered checkpointing

**Goal:** recover with minimal blast radius and prove the goodput gain.

Deliverables
- Policy engine with escalation ladder and guards; placer with failure-domain constraints.
- In-process recovery path (abort and re-init communicators; restore from tier 0), built
  on the M2 feasibility result, with a documented list of fault classes where it is and is
  not safe.
- Tier 0/1/2 checkpoint manager with atomic manifests, checksums, peer placement.
- Node replacement from spare pool; elastic shrink preserving global batch (Should).
- Correctness verification (sample ledger, loss comparison, optimizer/RNG state checks).
- 12 h+ goodput runs for goodput, B0, B1 (B2 if adopted) on the same fault schedule.

Exit criteria
- Metrics #7, #8, #10, #11 measured with phase decomposition; re-init-dominance
  hypothesis confirmed or refuted in writing.
- Goodput results reported across an MTBF sweep (EVALUATION §4.1).

`[OWNER-CORE]`: the recovery state machine and in-process re-init path.

---

## M6 — Simulator, write-up, public release

**Goal:** make the results legible in 90 seconds and reproducible by a stranger.

Deliverables
- Simulator calibrated and validated (EVALUATION §6); projection plots.
- README (problem, thesis, results table, architecture diagram, reproduce-in-an-hour).
- Architecture doc final; results report; blog post; demo recording; dataset card.
- Clean-room check: no third-party proprietary material; publication clearance for all
  hardware-derived data obtained.
- First tagged release (`v0.1.0`) with CHANGELOG entry.

Exit criteria
- Every number in README/blog links to a run id.
- A reviewer unfamiliar with the project reproduces the B0 vs goodput comparison on one
  fault class from the README.
