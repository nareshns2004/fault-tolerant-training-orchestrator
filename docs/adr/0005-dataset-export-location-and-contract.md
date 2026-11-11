# ADR-0005: Dataset export location, contract, and downstream artifacts

- Status: Accepted
- Date: 2026-10-11 (proposed); 2026-11-11 (revised and accepted)
- Deciders: maintainers

## Context
ARCHITECTURE §3.7 and ADR-0004 originally placed the dataset builder at `goodput/export/`,
reasoning that it is "an offline consumer of goodput's own schemas". But the exporter's
defining input is the faultlab ledger: every record joins an `Incident` (system output) with
its `FaultInjection` (ground truth), plus the rules `Verdict` (ARCHITECTURE §5). ADR-0004's
table names exactly one package as "the only place ground truth meets system output": `bench`.

The import-boundary test does not catch this. `FaultInjection` lives in `goodput.schemas`, so
`goodput/export/` could parse ledger JSONL without importing `faultlab`. The test would pass
while the guarantee ADR-0004 exists to provide ("could the classifier see ground truth?")
became a convention again.

The first draft of this ADR (2026-10-11) delegated the record schema and split logic to a
separate repository, `infra-incident-intel`. That repository no longer exists, and the
downstream plan has since narrowed: earlier drafts of the brief also named two models (a
ModernBERT classifier and a Qwen3 + LoRA reasoner). The labelled data cannot support that
much surface (OQ-17), and the docs told inconsistent stories.

## Options considered
1. **Keep `goodput/export/`.** No move. Cons: a ground-truth reader inside `goodput`;
   ADR-0004's guarantee holds only by convention. Cost to reverse: low.
2. **`bench/export/`, with the record schema owned in this repo.** The exporter sits where
   ADR-0004 already allows ledger + system output together. Cons: `bench` grows a second
   responsibility (evaluation and data publication), though both are "score system output
   against ground truth". Cost to reverse: low.
3. **Exporter in a separate downstream repo**, reading goodput artifacts. Cons: two-way
   dependency, and goodput could no longer test that its runs export cleanly. Cost to
   reverse: medium.

## Decision
Option 2.

**Location.** The exporter lives in `bench/export/`. `goodput` contains no code that reads
the ledger.

**Contract.** One JSON line per incident, defined by a JSON Schema owned by this repo
(`docs/schemas/incident.schema.json`, versioned, added with the M3 implementation) and
validated in a CPU test. Each record holds:
- time-ordered event lines, each with `ref = event_id`, rendered deterministically as
  `"<kind> " + " ".join(f"{k}={v}" for k, v in sorted(payload.items()))`;
- `labels`: ground-truth `fault_class` and culprit `ComponentRef` from the ledger;
- `system_verdict`: the rules `Verdict`;
- `provenance`: the label per ADR-0006 (routes records into real vs induced vs synthetic
  test splits);
- scrubbed hardware context from the env manifest (no hostnames, IPs or serials).

**Splits.** Records carry `split_keys` (`run_id`, `topology_group`, `fault_family`).
Splits group by run and hold out topologies; harvested `real` incidents are a separate test
split. Never split by random record (near-duplicate incidents from one trial would leak).

**Downstream artifacts: exactly these, and no separate repository.**

| Artifact | Kind | Role |
|---|---|---|
| goodput incident dataset | Dataset with a dataset card | The only training and evaluation source |
| `qwen3-nccl-rca-lora` | Hugging Face model | Grounded RCA: fault class, culprit, cited evidence lines |
| `nccl-incident-rca` | Hugging Face Space | Demo: signature matching (M3's catalogue) plus the model |

**Integration rule: recommends, never acts.** The model plugs in only behind
`goodput.signals.Classifier` and produces a `Verdict`. Every action still goes through the
policy engine's guards and the node agent's allowlisted executor. It replaces the rules
classifier only if it beats it on the same held-out split.

## Consequences
- Done in the same change: stub moved to `bench/export/`; ARCHITECTURE §3.7, §5, §8,
  README and PROJECT_BRIEF updated.
- Easier: one sentence answers "where can ground truth be read?" (`bench` and `faultlab`);
  one coherent downstream story.
- Harder: schema changes need a version bump and a dataset-card note.
- Implementation stays in M3 (MILESTONES "Dataset export v0"). This ADR records the location
  and contract so M1–M2 code doesn't grow in the wrong place.
- Revisit if the exporter ever needs to run online inside the controller (it should not), or
  if the dataset grows large enough that a second, encoder-based model adds measurable value.
