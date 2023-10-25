# goodput — Fault-tolerant training orchestrator

> Working name. "goodput" is the metric this project exists to move; rename freely.

## What this repo is

A cross-layer reliability system for multi-node LLM training. It injects realistic faults,
detects them fast, attributes them to the right component (rank, GPU, NIC, link, node,
storage), and recovers with the smallest possible blast radius using topology-aware,
tiered checkpoint-restart. The headline claim this repo must prove with measured numbers:
**higher training goodput under faults than stock PyTorch tooling, because attribution is
faster and more precise, not because we restart harder.**

It is one half of a two-project portfolio: this repo is "reliability at scale"; the sibling
repo (disaggregated inference engine with RDMA KV-cache transfer) is "efficiency at scale".
The labeled fault/telemetry dataset this repo produces feeds two downstream Hugging Face
models (a ModernBERT incident classifier and a Qwen3+LoRA root-cause reasoner).

## Who you are working with

Naresh — senior systems engineer, ~9 years across kernel networking, RDMA/RoCE, DPDK,
SR-IOV, KVM, NCCL and GPU infrastructure. Treat him as a peer; skip beginner explanations
of networking/kernel topics, but do explain PyTorch-internals and ML-side decisions.
Every line in this repo will be grilled by AI-lab and FAANG interviewers. Optimize for
**defensibility over velocity**. When you see a design choice he could not defend in an
interview, say so.

## Source-of-truth docs — read the relevant one before acting (do not bulk-load)

| Doc | Read when |
|---|---|
| `docs/PROJECT_BRIEF.md` | Any scope, priority, or "should we build X" question |
| `docs/ARCHITECTURE.md` | Before touching component boundaries, schemas, or interfaces |
| `docs/FAULT_MATRIX.md` | Anything in `faultlab/`, `signals/`, or `policy/` |
| `docs/EVALUATION.md` | Anything in `bench/`, any number that will be reported |
| `docs/MILESTONES.md` | Start of every session; planning; deciding "done" |
| `docs/INTERVIEW_DEFENSE.md` | After finishing a component; when running `/drill` |
| `docs/ENVIRONMENT.md` | Before any command that runs on real hardware |
| `docs/adr/` | Before re-opening a decision that already has an ADR |

## Operating rules (non-negotiable)

1. **Plan before code.** Every milestone and every non-trivial component starts with a
   written plan (use plan mode). Plans list: files touched, interfaces, test strategy,
   how the result will be measured, and open questions. Wait for Naresh's approval.
2. **Ownership boundaries.** Components tagged `[OWNER-CORE]` in `docs/MILESTONES.md` are
   written by Naresh. For those, you propose interfaces, write tests and fixtures, and
   review his implementation hard — you do not write the implementation unless he
   explicitly says "you write it" in that session. Everything else you may implement.
3. **No fabricated numbers.** Never write a latency, throughput, MTTR, accuracy, or goodput
   figure into any doc, README, comment, or commit message unless it came from a run
   under `bench/results/<run_id>/` with its environment manifest. If a number is a
   projection (simulator) or a literature value, label it as such with the source.
4. **Real vs induced vs synthetic.** Every fault and every telemetry sample is labeled
   `real` (hardware/OS actually misbehaved), `induced` (real mechanism, deliberately
   triggered, e.g. interposer-forced hang), or `synthetic` (injected telemetry values,
   e.g. DCGM field injection). Never blur these in code, data, or prose.
5. **Hardware safety.** Hosts are allowlisted in `docs/ENVIRONMENT.md`; never act on others.
   Every fault injection must have a registered revert and a timeout-based auto-revert.
   Never run without explicit, same-session confirmation from Naresh: GPU reset
   (`nvidia-smi -r`), firmware/driver changes, persistent clock/power changes without
   revert, switch configuration changes, reboot/power-off, `rm` outside the repo or
   `/scratch/goodput`, anything touching another user's jobs.
6. **Clean-room / IP.** This is a personal, public project. Never introduce code, configs,
   hostnames, IPs, internal tool names, log excerpts, or data originating from Naresh's
   employer or its internal POC. If a path, file, or pasted snippet looks like employer
   material, stop and ask. Published datasets must come only from hardware Naresh is
   cleared to use for public work (see `docs/ENVIRONMENT.md` → Provenance).
7. **Reuse before reinvent.** Prefer PyTorch DCP, the ProcessGroupNCCL flight recorder,
   torchtitan, DCGM, and (where it fits) NVIDIA Resiliency Extension. Novelty lives in
   cross-layer attribution, topology-aware policy, and measurement — not in re-writing
   what upstream already does well. Any "build it ourselves" choice needs an ADR.
8. **Scope discipline.** Must > Should > Stretch (see brief). Do not start a Stretch item
   while a Must item in the current milestone is open. Flag scope creep out loud.
9. **Tests.** Logic that can run on CPU (classifier, correlator, policy, state machine,
   schemas, ledger) must have CPU-only tests using recorded fixtures and `gloo`.
   GPU/multi-node tests are marked `@pytest.mark.gpu` / `@pytest.mark.multinode`.
   Fixtures are real captured logs/telemetry whenever possible, labeled per rule 4.
10. **Docs move with code.** Interface change → update `docs/ARCHITECTURE.md` in the same
    change. New decision → ADR. Milestone state → update "Current state" below.

## Commands (keep this list true; add as they come to exist)

```
make setup            # .venv (uv, py3.11) + dev deps + pre-commit
make check            # lint + typecheck + test (what CI runs)
make lint / fmt       # ruff check + format check / auto-fix
make typecheck        # mypy --strict on goodput, faultlab, bench
make test             # CPU-only unit + integration tests
make test-gpu         # single-node GPU tests
make env-manifest     # (stub) writes docs/ENVIRONMENT.md generated section + bench manifest
make topo             # (stub) topology discovery -> artifacts/topology.json
make bench SCENARIO=<path.yaml>   # (stub) runs an experiment, writes bench/results/<run_id>/
make report RUN=<run_id>          # (stub) regenerates plots/tables from raw results
```

## Code conventions

- Python ≥3.11, full type hints, `ruff` + `mypy --strict` on `goodput/`, `faultlab/`,
  `bench/`, `pytest`. Package import boundaries per ADR-0004.
- C/C++ (fault interposer, optional verbs replicator): C17/C++20, `-Wall -Wextra -Werror`,
  sanitizers in debug builds, no exceptions across the C ABI.
- All cross-component messages are versioned schemas (pydantic models in
  `goodput/schemas/`). Timestamps: monotonic for durations, UTC epoch-ns for correlation;
  document clock-sync assumptions (chrony/PTP) in ENVIRONMENT.
- Structured logs (JSON) only in `goodput/`; no bare prints.
- Config is declarative YAML validated by schema; no magic env vars without docs.
- Commits: conventional commits; one logical change per commit; message states *why*.

## Current state

- Milestone: **M1** (workload harness, baseline, topology discovery, environment manifest,
  prior-art review). Update this line when it changes.
- Repo skeleton in place (schemas, interfaces, CPU tests, CI); no measurements yet.
- Open decisions: ADR-0001–0004 are *Proposed*, not accepted. Review findings in
  `docs/OPEN_QUESTIONS.md` (OQ-1..OQ-19).
