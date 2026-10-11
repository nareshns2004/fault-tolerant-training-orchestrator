# ADR-0005: Dataset export location and contract

- Status: Proposed
- Date: 2026-10-11
- Deciders: Naresh (+ Claude Code as advisor)

## Context
ARCHITECTURE §3.7 and ADR-0004 place the Hugging Face dataset builder at `goodput/export/`,
reasoning that it is "an offline consumer of goodput's own schemas". But the exporter's
defining input is the faultlab ledger: every record joins an `Incident` (system output) with
its `FaultInjection` (ground truth), plus the rules `Verdict` (ARCHITECTURE §5). ADR-0004's
table names exactly one package as "the only place ground truth meets system output": `bench`.

The import-boundary test does not catch this. `FaultInjection` lives in `goodput.schemas`, so
`goodput/export/` can parse ledger JSONL without importing `faultlab`. The test passes while the
guarantee ADR-0004 exists to provide ("could the classifier see ground truth?") becomes a
convention again: a ground-truth reader would sit inside the system-under-test package.

The consumers now exist. The HF models live in a separate repo, `infra-incident-intel`, whose
`shared/` package defines the record format (incident schema v0.2) and publishes it as
`shared/incident.schema.json`. That repo never imports goodput.

## Options considered
1. **Keep `goodput/export/`** (status quo). No move. Cons: a ground-truth reader inside
   `goodput`; ADR-0004's guarantee holds only by convention. Cost to reverse: low.
2. **`bench/export/`.** The exporter sits where ADR-0004 already allows ledger + system
   output together. Cons: `bench` grows a second responsibility (evaluation and data
   publication), though both are "score system output against ground truth". Cost to reverse: low.
3. **Exporter in `infra-incident-intel`**, reading goodput artifacts. Cons: the HF repo would
   have to import goodput schemas (two-way dependency), and goodput could no longer test
   that its runs export cleanly. Cost to reverse: medium.

## Decision (proposed)
Option 2.
- Move the stub `goodput/export/__init__.py` to `bench/export/__init__.py`.
- **Contract:** one JSON line per incident, validated in a CPU test against a vendored copy of
  `infra-incident-intel/shared/incident.schema.json` (pinned by schema version). No Python
  dependency in either direction.
- **The exporter does not split.** It emits `split_keys` (`run_id`, `topology_group`,
  `fault_family`); splits are assigned downstream by `infra_incident.splits`, which groups by
  run and holds out topologies. This replaces "splits by scenario seed and node" in §5.
- **Mapping** (ledger → `labels`, events → time-ordered lines with `ref = event_id`, rules
  verdict → `system_verdict`, identifier masking downstream): see the HF repo's
  `shared/INCIDENT_SCHEMA.md` §"Mapping from goodput".
- Event rendering: `"<kind> " + " ".join(f"{k}={v}" for k, v in sorted(payload.items()))`, so
  output is deterministic.

## Consequences
- On acceptance, in the same change: move the stub; update ARCHITECTURE §3.7, §5 and §8,
  the README layout block and the ADR-0004 "Options" text; add the schema-validation test.
- Easier: one sentence answers "where can ground truth be read?" — `bench` and `faultlab`.
- Harder: schema changes need a coordinated version bump in both repos (the vendored JSON
  Schema makes a mismatch fail loudly instead of silently).
- Depends on OQ-2: `provenance.label` must be settled before the first export, because it
  routes incidents into `test_real` / `test_synthetic` downstream.
- Implementation stays in M3 (MILESTONES "Dataset export v0"). This ADR records only the
  location and contract, so M1–M2 code doesn't grow in the wrong place.
- Revisit if the exporter ever needs to run online inside the controller (it should not).
