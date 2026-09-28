# Security and safety policy

## Reporting a vulnerability

Please **do not** open a public issue. Report privately through GitHub's
"Report a vulnerability" (private security advisory) on this repository. If that isn't
available, email the maintainer at **TODO: maintainer contact**. We aim to acknowledge
reports within 7 days.

## Safety model for fault injection

`faultlab` deliberately breaks things: it kills processes, takes links down, and lowers
GPU clocks and power limits. The following invariants are enforced in code. Report any
way around them as a security issue.

| Invariant | Where |
|---|---|
| Default-deny host allowlist. A missing or empty allowlist allows nothing | `faultlab/safety.py` |
| Every fault declares `revert_timeout_s` (watchdog auto-revert) | `faultlab/scenario.py` |
| A fault's duration cannot exceed its revert timeout | `faultlab/scenario.py` |
| Destructive mechanisms need a per-fault `destructive: true` opt-in | `faultlab/scenario.py` |
| The revert is registered before host state changes (prepare → apply) | `faultlab/mechanisms/base.py` |
| The ledger is fsynced per record, and a startup sweep reverts stale injections | `faultlab/ledger.py` |

The following are **never** automated and always need a human to confirm at the time:
GPU reset, firmware or driver changes, switch configuration changes, reboot or power-off,
and anything that touches other users' jobs.

Never run faultlab on shared or production clusters you don't control.

## Data

Published datasets and fixtures must come only from hardware cleared for public use. Scrub
hostnames, IP addresses, serial numbers and usernames from all captured data before
committing it.
