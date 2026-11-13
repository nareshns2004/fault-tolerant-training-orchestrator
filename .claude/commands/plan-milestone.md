---
description: Write a plan for a milestone (or one deliverable of it) and stop for approval
argument-hint: <milestone, e.g. M1b or "M2 ledger writer">
---

Plan **$ARGUMENTS** for goodput. Do not edit any file except the plan itself.

1. Read `docs/MILESTONES.md` (the section for $ARGUMENTS), then only the docs it depends on:
   `docs/ARCHITECTURE.md` for interfaces, `docs/FAULT_MATRIX.md` for faults,
   `docs/EVALUATION.md` for anything measured, `docs/OPEN_QUESTIONS.md` and `docs/adr/`
   for decisions already made. Do not re-open a decision that has an Accepted ADR.
2. Write the plan to `.local/plans/<milestone>-<yyyy-mm-dd>.md` (gitignored) with:
   - **Scope:** the deliverables and exit criteria you will close, quoted from MILESTONES.
   - **Files:** every file to add or change, one line each on why.
   - **Interfaces:** signatures and schema changes (schema changes bump `schema_v`).
   - **`[OWNER-CORE]` split:** what the maintainer implements versus what you will write
     (interfaces, tests, fixtures, review).
   - **Tests:** the CPU tests (gloo, recorded fixtures) and any `gpu`/`multinode` tests.
   - **Measurement:** how each result will be measured, which `bench/results/<run_id>/`
     it lands in, and the sample size it needs under EVALUATION §4.1.
   - **Hardware actions:** every command that touches real hosts, with its revert.
   - **Open questions:** anything that blocks the plan, with a proposed answer.
3. Print the plan and **stop**. Wait for the maintainer's approval before writing code.
