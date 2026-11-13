# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses
[Semantic Versioning](https://semver.org/) once it reaches 0.1.0.

## [Unreleased]

### Added
- Incident record contract `bench/export/record.py` and its generated JSON Schema
  `docs/schemas/incident.schema.json` (`make schemas`; a CPU test fails on drift). Hostnames
  and GPU UUIDs are rejected at validation time.
- ADR-0007: OQ-10, 11, 13, 14, 15, 17, 18 and 20 resolved; downstream HF artifacts amended
  (incident records ship inside the model repo).
- `/plan-milestone` and `/drill` Claude Code commands.
- README visual identity: generated light/dark banner and architecture diagrams
  (`scripts/build_assets.py`), Mermaid state diagram, social-preview card, badge row and
  navigation; CI fails if the committed graphics drift from their generator.
- Fixed: code-of-conduct contact placeholder now points to private reporting.
- Repository skeleton: `goodput`, `faultlab` and `bench` packages; versioned schemas;
  component interfaces; a CPU-only test suite; and contributor and security docs.
- GitHub Actions CI (ruff, mypy --strict, CPU tests, scenario validation, build, repo
  hygiene), pre-commit config, PR and issue templates, Dependabot.
- ADR-0005 revised and accepted (export moves to `bench/export/`; one model, one Space; no
  separate downstream repo), ADR-0006 (provenance labels).
- `docs/prior_art.md` draft, including NVRx's experimental attribution module.
- EVALUATION: system-agnostic TTD/TTR, B0-tuned baseline, sample-size rules.

### Changed
- ADR-0001, 0002 and 0004 accepted; ADR-0002 now records HTTP/JSON and the c10d-store lease.
- PyPI distribution renamed `goodput-train` (`goodput` is taken); import package and CLI
  unchanged.
- PROJECT_BRIEF §6: every metric lists its fault IDs; metric 8 falls back to elastic
  shrink (now Must) when no spare node exists. M1b runs SIGKILL trials only.
- FAULT_MATRIX: faultlab-scheduled faults relabelled `I` (ADR-0006).
- MILESTONES: M1 split into M1a (CPU, prior art) and M1b (cluster baselines); in-process
  restart feasibility spike moved to M2.
- PROJECT_BRIEF: claimed gap narrowed to fabric attribution, topology join and policy;
  targets restated so they can be demonstrated at the planned sample sizes.

### Removed
- Committed `__pycache__` files; added `.gitignore`.
