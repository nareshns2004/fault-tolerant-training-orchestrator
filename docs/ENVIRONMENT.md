# Environment — goodput

## Manual section (Naresh fills before any hardware run)

- Host allowlist (hostnames Claude Code may act on):
  - TODO
  - Machine-readable copy for faultlab: `configs/hosts.local.yaml` (gitignored; format in
    `configs/hosts.example.yaml`). Keep the two in sync; faultlab reads only the YAML.
- Nodes × GPUs per node, GPU model:
- Interconnect: IB or RoCE? NIC model(s), ports per node, rails:
- Switch(es) and whether config access exists (yes/no — assume no):
- Shared storage for tier-2 checkpoints (type, mount path, expected bandwidth):
- Scratch path (`/scratch/goodput` or other):
- Scheduler: bare metal / Slurm / Kubernetes:
- Clock sync: chrony / PTP, expected skew:
- Spare nodes available for replacement experiments:
- **Provenance / clearance:** who owns this hardware; written confirmation that it may be
  used for a personal public project and that data collected on it may be published: TODO

## Generated section (`make env-manifest` overwrites below this line)
<!-- GENERATED:BEGIN -->
<!-- GENERATED:END -->
