# goodput: guidance for AI coding agents

This file is read automatically by Claude Code (and is useful to any coding agent or new
contributor). Human contributors should start with [CONTRIBUTING.md](CONTRIBUTING.md).

## What this repo is

**goodput** (GitHub Project 1; repository `goodput-fault-tolerant-training-orchestrator`;
PyPI distribution `goodput-train`) is a cross-layer
reliability system for multi-node LLM training. It injects realistic faults, detects them
fast, attributes them to the right component (rank, GPU, NIC, port, link, node, storage),
and recovers with the smallest possible blast radius using topology-aware, tiered
checkpoint-restart. The claim it exists to test with measured numbers: **higher training
goodput under faults than stock PyTorch tooling, because attribution is faster and more
precise, not because we restart harder.**

### Where it sits

goodput is one of two repos in one portfolio; keep them consistent:

- **GitHub Project 1: goodput** (this repo): reliability at scale.
- **GitHub Project 2: kvwire** (repository `kvwire-disaggregated-inference-engine`):
  RDMA KV-cache transport for disaggregated inference; efficiency at scale.
- **Hugging Face Project 1**, built only from this repo's data: model
  `qwen3-nccl-rca-lora` (slow tier, structured verdict citing evidence refs; train/eval data
  ships *inside* the model repo) and Space `nccl-incident-rca` (fast tier, signature matching).
- **Hugging Face Project 2**, built only from kvwire's data: dataset `rdma-kv-transfer-traces`
  and Space `disagg-kv-explorer`.

There is exactly one HF model and one HF dataset across the portfolio, no third repo, and no
encoder classifier ([ADR-0005](docs/adr/0005-dataset-export-location-and-contract.md),
[ADR-0007](docs/adr/0007-open-questions-resolved.md)). The model plugs back in behind
`goodput.signals.Classifier` and only *recommends*; it never acts. The export contract is
`bench/export/record.py` → `docs/schemas/incident.schema.json` (`make schemas`).

## Maintainers and calibration

The maintainer has a kernel-networking / RDMA / NCCL / GPU-infrastructure background: skip
beginner explanations of networking and kernel topics, but do explain PyTorch-internals
and ML-side decisions. Optimize for **defensibility over velocity**: when a design choice
could not be defended to a skeptical reviewer, say so.

## Source-of-truth docs: read the relevant one before acting (do not bulk-load)

| Doc | Read when |
|---|---|
| `docs/PROJECT_BRIEF.md` | Any scope, priority, or "should we build X" question |
| `docs/prior_art.md` | Any claim about what existing tools do or don't cover |
| `docs/ARCHITECTURE.md` | Before touching component boundaries, schemas, or interfaces |
| `docs/FAULT_MATRIX.md` | Anything in `faultlab/`, `signals/`, or `policy/` |
| `docs/EVALUATION.md` | Anything in `bench/`, any number that will be reported |
| `docs/MILESTONES.md` | Start of every session; planning; deciding "done" |
| `docs/OPEN_QUESTIONS.md` | Before writing code that depends on an unresolved decision |
| `docs/ENVIRONMENT.md` | Before any command that runs on real hardware |
| `docs/adr/` | Before re-opening a decision that already has an ADR |

## Operating rules (non-negotiable)

1. **Plan before code.** Every milestone and every non-trivial component starts with a
   written plan (use plan mode). Plans list: files touched, interfaces, test strategy,
   how the result will be measured, and open questions. Wait for maintainer approval.
2. **Ownership boundaries.** Components tagged `[OWNER-CORE]` in `docs/MILESTONES.md` are
   implemented by the maintainer. For those, you propose interfaces, write tests and
   fixtures, and review the implementation hard. You do not write the implementation
   unless the maintainer explicitly says "you write it" in that session. Everything else
   you may implement.
3. **No fabricated numbers.** Never write a latency, throughput, MTTR, accuracy, or goodput
   figure into any doc, README, comment, or commit message unless it came from a run
   under `bench/results/<run_id>/` with its environment manifest. Projections (simulator),
   calculations and literature values are labelled as such, with the source.
4. **Real vs induced vs synthetic.** Every fault and every telemetry sample is labelled
   `real` (hardware/OS genuinely misbehaved, harvested, not scheduled by us), `induced`
   (real mechanism, deliberately triggered: SIGKILL, interposer hang, `ip link set down`),
   or `synthetic` (fabricated values, e.g. DCGM field injection). Never blur these in code,
   data, or prose. See [ADR-0006](docs/adr/0006-provenance-labels.md).
5. **Hardware safety.** Hosts are allowlisted in `docs/ENVIRONMENT.md`; never act on others.
   Every fault injection must have a registered revert and a timeout-based auto-revert.
   Never run without explicit, same-session confirmation from the maintainer: GPU reset
   (`nvidia-smi -r`), firmware/driver changes, persistent clock/power changes without
   revert, switch configuration changes, reboot/power-off, `rm` outside the repo or
   `/scratch/goodput`, anything touching another user's jobs.
6. **Clean-room / IP.** This is a public project. Never introduce code, configs,
   hostnames, IPs, internal tool names, log excerpts, or data from any employer or third
   party. If a path, file, or pasted snippet looks like proprietary material, stop and
   ask. Published datasets must come only from hardware cleared for public work (see
   `docs/ENVIRONMENT.md` → Provenance).
7. **Reuse before reinvent.** Prefer PyTorch DCP, the ProcessGroupNCCL flight recorder,
   torchtitan, DCGM, and (where it fits) NVIDIA Resiliency Extension, including its
   flight-recorder attribution (`docs/prior_art.md`). Novelty lives in fabric-layer
   attribution, the topology join, topology-aware policy, and measurement, not in
   re-writing what upstream already does well. Any "build it ourselves" choice needs an ADR.
8. **Scope discipline.** Must > Should > Stretch (see brief). Do not start a Stretch item
   while a Must item in the current milestone is open. Flag scope creep out loud.
9. **Tests.** Logic that can run on CPU (classifier, correlator, policy, state machine,
   schemas, ledger) must have CPU-only tests using recorded fixtures and `gloo`.
   GPU/multi-node tests are marked `@pytest.mark.gpu` / `@pytest.mark.multinode`.
   Fixtures are real captured logs/telemetry whenever possible, labelled per rule 4.
10. **Docs move with code.** Interface change → update `docs/ARCHITECTURE.md` in the same
    change. New decision → ADR. Milestone state → update "Current state" below.

## Commands (keep this list true; add as they come to exist)

```
make setup            # .venv (uv, py3.11) + dev deps + pre-commit
make check            # lint + typecheck + test (what CI runs)
make lint / fmt       # ruff check + format check / auto-fix
make typecheck        # mypy --strict on goodput, faultlab, bench
make test             # CPU-only unit + integration tests
make schemas          # regenerate docs/schemas/*.json (a test fails on drift)
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
- Commits: conventional commits, DCO sign-off; one logical change per commit; message
  states *why*.
- Personal, local-only notes go in `.local/` or `CLAUDE.local.md` (both gitignored), never
  in tracked files.

## Slash commands

- `/plan-milestone <M>`: writes a plan to `.local/plans/` and stops for approval.
- `/drill [component]`: five interview questions on a finished component, graded against
  the repo.

## Current state

- Milestone: **M1a** (scaffold, CPU harness, prior-art gate, environment). Update this
  line when it changes.
- Repo skeleton in place (schemas, interfaces, CPU tests, CI, incident-record contract);
  no measurements yet.
- ADRs: 0001, 0002, 0004–0007 *Accepted*; 0003 *Proposed* until the prior-art gap analysis
  (`[OWNER-CORE]`) is written.
- Only open question: OQ-1 (target hardware, `docs/ENVIRONMENT.md`). M1a exit needs it and
  the gap analysis.
- Next public artifact: the B0 SIGKILL TTR phase decomposition (M1b).
