# Test fixtures

These are recorded logs, telemetry and flight-recorder dumps used by the CPU tests.

Every fixture directory has a `PROVENANCE.yaml` that records:

```yaml
label: real | induced | synthetic      # CLAUDE.md rule 4
captured_on: <hardware class, never a hostname>
captured_utc: 2026-01-01T00:00:00Z
versions: { pytorch: ..., nccl: ..., driver: ..., rdma_core: ... }
scenario: <faultlab scenario id, if induced>
notes: ...
```

Rules:
- Real captures come only from hardware cleared for public use
  (docs/ENVIRONMENT.md → Provenance). Scrub hostnames, IPs and serials first.
- Hand-written fixtures are `synthetic`, whatever they imitate.
- Keep each fixture small, under 1 MB (enforced by pre-commit). Put bulk data in
  `bench/results/`.
