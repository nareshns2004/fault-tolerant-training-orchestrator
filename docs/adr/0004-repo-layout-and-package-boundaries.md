# ADR-0004: Repository layout and package boundaries

- Status: Proposed
- Date: 2026-09-28
- Deciders: Naresh (+ Claude Code as advisor)

## Context
ARCHITECTURE §8 (original) had `faultlab/`, `bench/`, `sim/` and `export/` as top-level
directories next to the `goodput/` package, and ran `mypy --strict` on `goodput/` only.
That leaves three problems:

1. **Ground-truth leakage.** If the detector can import the fault ledger, attribution
   results can be contaminated by ground truth, even by accident (for example a test helper
   reading the ledger). Interviewers will ask how we know the classifier never saw the
   answer.
2. **Unchecked safety code.** faultlab holds the revert and watchdog logic, the most
   safety-critical Python in the repo, yet it was outside `mypy --strict`.
3. **Import-name pollution.** Top-level Python packages called `export` and `sim` are too
   generic.

## Options considered
1. **Everything under `goodput/`** (`goodput.faultlab`, `goodput.bench`). One namespace,
   but the boundary between system under test and ground truth becomes a convention, not a
   structure.
2. **Three packages in one distribution: `goodput` (system under test), `faultlab`
   (adversary + ground truth), `bench` (evaluator).** `sim` and `export` move into
   `goodput`, since they are offline consumers of goodput's own schemas. A CPU test
   enforces the import rules.
3. **Separate repos or distributions.** Strongest isolation, but costly to keep in sync
   this early.

Cost to reverse: low. Moving to option 1 or 3 later is a mechanical move.

## Decision
Option 2. Import rules:

| Package | May import |
|---|---|
| `goodput` | itself only (never `faultlab`, never `bench`) |
| `faultlab` | `goodput.schemas` only |
| `bench` | `goodput`, `faultlab` (it is the only place ground truth meets system output) |

`tests/unit/test_import_boundaries.py` enforces these rules, and `mypy --strict` covers
all three packages. Non-Python assets stay next to their owners: `faultlab/interposer/`
(C), `faultlab/scenarios/`, `bench/scenarios/` and `bench/results/`.

The privilege split follows the same line. faultlab needs rights to change host state;
the goodput agent only reads.

## Consequences
- Easier: a clear answer to "could the classifier see ground truth?", and strict typing
  on the safety-critical code.
- Harder: shared helpers must live in `goodput.schemas` or be duplicated.
- `bench/results/` sits inside a Python package directory. It is excluded from the wheel
  and gitignored except for `summary/`.
- Revisit if faultlab needs its own release cadence (then use option 3).
