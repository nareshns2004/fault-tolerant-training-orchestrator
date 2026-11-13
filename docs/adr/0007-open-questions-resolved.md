# ADR-0007: Remaining open questions resolved, and the downstream-artifact plan

- Status: Accepted
- Date: 2026-11-13
- Deciders: maintainers
- Resolves: OQ-10, OQ-11, OQ-13, OQ-14, OQ-15, OQ-17, OQ-18, OQ-20

## Context
After ADR-0006 and the M1 split, eight review findings were still open in
`docs/OPEN_QUESTIONS.md`. None needs hardware to decide, and several were blocking writing
the M1b plan (how to time a stock baseline, which faults M1b may run) or the M3/M5 plans
(which faults a metric covers, how the controller lease works). Separately, the
portfolio this repo belongs to was re-scoped. It now has exactly two GitHub repos (goodput,
reliability; kvwire, efficiency) and exactly one Hugging Face model and one dataset in
total. The dataset slot belongs to kvwire's `rdma-kv-transfer-traces`, so goodput's
labelled incidents cannot be a separate Hugging Face dataset as ADR-0005 assumed.

OQ-1 (target hardware) stays open. It is the only remaining blocker, and only the
maintainer can resolve it.

## Decisions

| OQ | Decision |
|---|---|
| OQ-10 | B0 is instrumented **without modification**: a wrapper records wall-clock timestamps around `torchrun` and the training script's existing step log, and `bench` parses torchrun agent logs and `NCCL_DEBUG=INFO` output for phase boundaries. Phases a stock baseline cannot expose are reported as merged (for example "process start + CUDA init"), never estimated. |
| OQ-11 | M1b runs **SIGKILL trials only** (F01 and node-level SIGKILL of all ranks). Link-down and every other fault with host-state side effects wait for faultlab's registered revert and watchdog (M2). |
| OQ-13 | Every metric in PROJECT_BRIEF §6 lists its fault IDs. Metric 7 (in-process path, transient faults) covers **F01, F02, F03, F11**. Metric 8 (loss of a node or its fabric attachment) covers **F08, F12, F16**. |
| OQ-14 | The tier-0 snapshot interval is **configuration**, not a constant. Metric 9 is reported as overhead **per interval** across a sweep (at least every step, every 10 steps, and the Young/Daly interval), so no reader has to guess the frequency. |
| OQ-15 | If no spare node exists, metric 8 is measured as **elastic shrink** (continue at reduced world size from peer tier-1 state), and elastic shrink is promoted from Should to **Must**. Replacement from a spare is reported only when a spare is actually available. |
| OQ-17 | (a) Any "≥ 95%" claim needs **≥ 60 trials per Must class** (Wilson 95% lower bound reported, EVALUATION §4.1). (b) Splits hold out by **seed and by node** (`split_keys`), plus the harvested-real split. (c) There is **one** downstream model, `qwen3-nccl-rca-lora`, emitting structured verdicts that cite evidence `ref`s, and no encoder classifier. (d) Its train/val/test data ships **inside the model repo** (`data/`, `eval/`, scoring script), not as a separate dataset. (e) It ships only if it beats the rules classifier, the zero-shot base model and the per-class majority baseline on the same held-out split; otherwise the card says so and the Space shows signature matching only. |
| OQ-18 | Control-plane transport is **HTTP/JSON** carrying the existing pydantic schemas (no gRPC). Rendezvous and membership use the **c10d `TCPStore`** that torchrun's c10d rendezvous already runs. The controller **lease** is a key in that store holding `(holder, epoch, expires_utc_ns)`, acquired and renewed with `compare_set`. A challenger may take over only after expiry plus a clock-skew margin taken from ENVIRONMENT, and every cluster-wide action carries the lease epoch so a deposed controller's actions are rejected. etcd is the documented upgrade path if the store host becomes a measured single point of failure. ADR-0002 is amended accordingly. |
| OQ-20 | Public name **goodput** everywhere: the GitHub repository is renamed `goodput` (GitHub redirects the old URL); the import package and CLI stay `goodput`. The PyPI name `goodput` is taken, so the **distribution** is `goodput-train` (free when checked, 2026-11-13). |

## Downstream artifacts (amends ADR-0005)

| Artifact | Built from | Role |
|---|---|---|
| `nareshns2004/qwen3-nccl-rca-lora` (HF model) | `bench/export/` records | Slow tier: Qwen3 + LoRA, structured verdict with evidence refs. Repo holds `data/`, `eval/`, training and scoring code, and the card's data section. |
| `nareshns2004/nccl-incident-rca` (HF Space) | M3 signature catalogue + the model | Fast tier: signature matching. Slow tier shown only once the model passes its gates. |

The incident record contract is `bench/export/record.py` → `docs/schemas/incident.schema.json`.
Nothing is uploaded to either repo until real exported records exist (labelled per ADR-0006).

## Options considered (abbreviated: the individual findings list the alternatives)
- OQ-18: gRPC (typed, but a second schema language beside pydantic); etcd from day one
  (more robust, but adds an external service at tens of GPUs). Rejected for M1–M5;
  revisit with measured failure data.
- OQ-17: a separate HF dataset for incidents (conflicts with the one-dataset portfolio rule
  and would publish thin data on its own); a second encoder model (the data cannot support
  two models).
- OQ-20: keep the long repository name (it describes orchestration, which is not the
  contribution).

## Consequences
- PROJECT_BRIEF §6 and §9, EVALUATION §1.1 and §4.2, MILESTONES M1b/M5, ARCHITECTURE §3.3
  and §6, ADR-0002, ADR-0005, README and CLAUDE.md are updated in the same change.
- ADR-0001, ADR-0002 and ADR-0004 move to Accepted. ADR-0003 stays Proposed until the
  prior-art gap analysis (M1a, `[OWNER-CORE]`) is written.
- Revisit OQ-15 when a spare node exists; revisit OQ-18 if lease or store failures show up
  in M5 measurements.
