# Contributing to goodput

Thanks for your interest. This project is judged on how rigorous its evidence is, so the
rules below are stricter than most. They exist so that every claim in this repo can be
defended.

## Ground rules

1. **No number without a run.** Do not put any latency, throughput, MTTR, accuracy or
   goodput figure in code comments, docs or commit messages unless it comes from
   `bench/results/<run_id>/`. Label projections and literature values, and cite the
   source.
2. **Label provenance.** Every fault and telemetry sample is `real`, `induced` or
   `synthetic` (see `goodput.schemas.Provenance`). Never mix them.
3. **Safety first.** faultlab acts only on allowlisted hosts. Every injection needs a
   revert and a timeout-based auto-revert. Destructive mechanisms need explicit opt-in.
   See [SECURITY.md](SECURITY.md).
4. **Clean-room.** Contribute only code and data you have the right to publish. Do not add
   proprietary code, internal hostnames or IPs, logs or data from any employer or third
   party.
5. **Reuse before reinventing.** Prefer PyTorch DCP, the flight recorder, torchtitan, DCGM
   and NVRx. A decision to build something ourselves needs an ADR.

## Development setup

You need Linux, Python ≥ 3.11 and [uv](https://github.com/astral-sh/uv). No GPU is needed
for the core test suite.

```bash
make setup    # .venv + dev deps + pre-commit hooks
make check    # ruff, mypy --strict, CPU tests: exactly what CI runs
```

GPU and multi-node tests are opt-in: `make test-gpu` and `make test-multinode`. They
only run on allowlisted hosts.

## Code conventions

- **Python ≥ 3.11**, with full type hints. `mypy --strict` must pass for `goodput`,
  `faultlab` and `bench`.
- **ruff** handles linting and formatting (line length 100).
- **Structured JSON logs only.** Use `goodput.logs.get_logger`; `print()` is lint-banned in
  the packages.
- **Messages between components** are versioned pydantic models in `goodput/schemas/`.
  A breaking change bumps `schema_v`.
- **Timestamps** are `*_utc_ns` for correlating across hosts and `*_mono_ns` for durations
  on one host. Never mix them.
- **Package boundaries** ([ADR-0004](docs/adr/0004-repo-layout-and-package-boundaries.md)):
  `goodput` never imports `faultlab` or `bench`, and `faultlab` imports only
  `goodput.schemas`. `tests/unit/test_import_boundaries.py` enforces this.
- **C code** (the interposer) is C17 with `-Wall -Wextra -Werror`, sanitizers in debug
  builds, and no `longjmp` or exceptions across the C ABI.

## Tests

- Logic that can run on CPU (classifier, correlator, policy, state machine, schemas,
  ledger) must have CPU-only tests. Use recorded fixtures and the `gloo` backend.
- Mark hardware tests with `@pytest.mark.gpu` or `@pytest.mark.multinode`.
- Fixtures follow [tests/fixtures/README.md](tests/fixtures/README.md). Each one needs a
  `PROVENANCE.yaml`, and hand-written fixtures are labelled `synthetic`.
- A behavioural spec for code that doesn't exist yet uses
  `xfail(strict=True, raises=NotImplementedError)`. That way it fails loudly, instead of
  passing silently, once the code lands.

## Documentation moves with code

- Changing an interface or schema → update `docs/ARCHITECTURE.md` in the same PR.
- Making a new design decision → add an ADR in `docs/adr/`, starting from
  `0000-template.md`.
- Adding or changing a metric → `docs/EVALUATION.md` is the only place metrics are
  defined.

## Commits and pull requests

- Use [Conventional Commits](https://www.conventionalcommits.org/) (`feat(faultlab): ...`,
  `fix(schemas): ...`, `docs(adr): ...`). Make one logical change per commit. The message
  says *why*.
- **Sign off every commit** (`git commit -s`) to certify the
  [Developer Certificate of Origin](https://developercertificate.org/). The sign-off is
  the project's record of where each contribution came from.
- Fill in the PR template checklist. Reviewers will ask where any number came from.
