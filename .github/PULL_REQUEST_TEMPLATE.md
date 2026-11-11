## What and why

<!-- One logical change. Say *why*, not just what. Link the issue / ADR / open question. -->

## Checklist

- [ ] `make check` passes locally (ruff, mypy --strict, CPU tests).
- [ ] **No number without a run.** Any latency / MTTR / accuracy / goodput figure added in
      code, docs or this description links to `bench/results/<run_id>/`. Projections and
      literature values are labelled as such, with a source.
- [ ] **Provenance.** Every new fault, fixture or telemetry sample is labelled `real`,
      `induced` or `synthetic` (`goodput.schemas.Provenance`); fixtures have a `PROVENANCE.yaml`.
- [ ] **Package boundaries** (ADR-0004) still hold: `goodput` does not import `faultlab`/`bench`.
- [ ] **Safety.** New fault mechanisms register a revert before applying, honour the host
      allowlist, and require `destructive: true` where applicable (SECURITY.md).
- [ ] **Docs move with code.** Interface/schema change → `docs/ARCHITECTURE.md`; new
      decision → ADR; metric change → `docs/EVALUATION.md` only.
- [ ] Commits are signed off (`git commit -s`, DCO).
