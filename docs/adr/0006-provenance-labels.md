# ADR-0006: Meaning of the real / induced / synthetic provenance labels

- Status: Accepted
- Date: 2026-11-11
- Deciders: maintainers
- Resolves: OQ-2

## Context
`docs/FAULT_MATRIX.md` labelled F01, F08, F09, F10, F13, F14, F16 and F18 as **R** (real),
yet every one of them is triggered on purpose by faultlab. The contributor rules, the
`goodput.schemas.Provenance` docstring and the tests already defined deliberately triggered
real mechanisms (SIGKILL, `ip link set down`) as **induced**. The matrix was the outlier.
It was also unclear what a label means on a telemetry *sample* as opposed to a *fault*.
This blocked the M2 ledger.

## Options considered
1. **Keep R for "real mechanism".** Matches the matrix, but makes "real" mean two things
   (scheduled vs genuinely occurring), which is exactly the blur rule 4 forbids.
2. **R only for harvested faults; anything faultlab schedules is I or S.** One meaning per
   label; consistent with the schema and tests.

## Decision
Option 2.

- **On a `FaultInjection`:** `real` = harvested (hardware/OS misbehaved without being
  scheduled; `scenario_id` is `None`). `induced` = a real mechanism deliberately triggered
  by faultlab. `synthetic` = fabricated values (e.g. DCGM field injection).
- **On a `TelemetrySample`:** the label describes the *value's* origin. A counter genuinely
  read from hardware during an induced fault is `real`; the fault's own label lives on its
  `FaultInjection`.

All faultlab-scheduled rows in `docs/FAULT_MATRIX.md` are relabelled **I** (or **S** for
fabricated telemetry). **R** appears only on records harvested into `bench/real_faults/`.

## Consequences
- The dataset and every report can split results cleanly into harvested vs induced vs
  synthetic, and never present induced results as field failure rates.
- Ledger code needs no change; the schema already encoded this interpretation.
- Revisit only if a new mechanism blurs the line (e.g. load that triggers a genuine
  hardware fault): such a fault is recorded as `real` with the scheduled injection
  referenced in its evidence.
