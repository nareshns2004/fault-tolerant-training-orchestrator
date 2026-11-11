# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses
[Semantic Versioning](https://semver.org/) once it reaches 0.1.0.

## [Unreleased]

### Added
- Repository skeleton: `goodput`, `faultlab` and `bench` packages; versioned schemas;
  component interfaces; a CPU-only test suite; and contributor and security docs.
- GitHub Actions CI (ruff, mypy --strict, CPU tests, scenario validation, build, repo
  hygiene), pre-commit config, PR and issue templates, Dependabot.
- ADR-0005 revised and accepted (export moves to `bench/export/`; one model, one Space; no
  separate downstream repo), ADR-0006 (provenance labels).
- `docs/prior_art.md` draft, including NVRx's experimental attribution module.
- EVALUATION: system-agnostic TTD/TTR, B0-tuned baseline, sample-size rules.

### Changed
- FAULT_MATRIX: faultlab-scheduled faults relabelled `I` (ADR-0006).
- MILESTONES: M1 split into M1a (CPU, prior art) and M1b (cluster baselines); in-process
  restart feasibility spike moved to M2.
- PROJECT_BRIEF: claimed gap narrowed to fabric attribution, topology join and policy;
  targets restated so they can be demonstrated at the planned sample sizes.

### Removed
- Committed `__pycache__` files; added `.gitignore`.
