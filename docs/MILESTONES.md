# Milestones — goodput

IDs M1–M6 match the portfolio tracker (P1). A milestone is done only when every exit
criterion is met with evidence (run ids, test names, docs). `[OWNER-CORE]` = Naresh writes
the implementation; Claude Code designs interfaces, writes tests/fixtures, and reviews.

---

## M1 — Workload harness, baselines, topology, prior-art gate

**Goal:** a measured, reproducible "before" picture and a validated reason to exist.

Deliverables
- Repo scaffold, `make setup/test`, CI running CPU tests.
- `make env-manifest` and `make topo` producing `docs/ENVIRONMENT.md` generated section and
  `artifacts/topology.json` (rank → GPU → NUMA → NIC/port → rail → switch where discoverable).
- torchtitan workload running at 1B (iteration) and 8B (headline) with FSDP2 on ≥ 2 nodes;
  step time and MFU recorded.
- Baselines B0 and B1 implemented; manual SIGKILL and link-down trials measured with
  MTTR phase decomposition (instrument phases even for the baseline).
- `docs/prior_art.md`: MegaScale, Llama 3 reliability section, Meta ETTR paper, GEMINI,
  CheckFreq, torchft, NVRx, PyTorch flight recorder — each with: mechanism, what it covers,
  what it leaves open, what we reuse. Ends with a go/re-scope decision on the claimed gap.
- Revisit targets in PROJECT_BRIEF §6 with baseline data; record changes in an ADR.

Exit criteria
- A stranger could reproduce the B0 run from docs alone.
- Baseline MTTR decomposition exists for ≥ 2 fault types with ≥ 5 trials each.
- ADR-0001/0002/0003 accepted or revised.
- Prior-art gate decision written.

`[OWNER-CORE]`: the MTTR phase instrumentation design; the prior-art gap analysis.

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

Exit criteria
- Each Must fault injected ≥ 20 times with 100% ledger completeness and 100% verified revert.
- Poisson fault scheduler produces a replayable schedule from a seed.

`[OWNER-CORE]`: the NCCL interposer hang/mismatch logic; revert/watchdog design.

---

## M3 — NCCL/PyTorch signature capture + culprit attribution

**Goal:** name the culprit rank for hangs, crashes, desyncs, and transport errors — fast.

Deliverables
- Flight recorder enabled and dumps collected from all ranks on trigger and on demand.
- Cross-rank analyzer: aligns per-rank collective sequences, identifies ranks that never
  entered / never completed / diverged; combines with progress beacons.
- Rules classifier v1 for F01–F04, F11; `Verdict` with evidence references.
- Signature catalogue (`docs/signatures.md`): per class, the observable fingerprint and why.
- Dataset export v0 (feeds HF1), with provenance labels and leakage-safe splits.

Exit criteria
- Metrics #2, #3 in PROJECT_BRIEF met or the gap explained with data.
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

`[OWNER-CORE]`: RDMA counter semantics and anomaly rules (this is the moat — must be his).

---

## M5 — Topology-aware recovery + tiered checkpointing

**Goal:** recover with minimal blast radius and prove the goodput gain.

Deliverables
- Policy engine with escalation ladder and guards; placer with failure-domain constraints.
- In-process recovery path (abort and re-init communicators; restore from tier 0) with a
  documented list of fault classes where it is and is not safe.
- Tier 0/1/2 checkpoint manager with atomic manifests, checksums, peer placement.
- Node replacement from spare pool; elastic shrink preserving global batch (Should).
- Correctness verification (sample ledger, loss comparison, optimizer/RNG state checks).
- 12 h+ goodput runs for goodput, B0, B1 (B2 if adopted) on the same fault schedule.

Exit criteria
- Metrics #7, #8, #10, #11 measured with phase decomposition; re-init-dominance
  hypothesis confirmed or refuted in writing.

`[OWNER-CORE]`: the recovery state machine and in-process re-init path.

---

## M6 — Simulator, write-up, public release

**Goal:** make the results legible in 90 seconds and defensible for 90 minutes.

Deliverables
- Simulator calibrated and validated (EVALUATION §6); projection plots.
- README (problem, thesis, results table, architecture diagram, reproduce-in-an-hour).
- Architecture doc final; results report; blog post; demo recording; dataset card.
- `docs/INTERVIEW_DEFENSE.md` rehearsed: Naresh can answer every question without notes.
- Clean-room check: no employer material; public-release clearance obtained.

Exit criteria
- Every number in README/blog links to a run id.
- A reviewer unfamiliar with the project reproduces the B0 vs goodput comparison on one
  fault class from the README.
