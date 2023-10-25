# Fault Matrix — goodput

Each row is a fault class the system must inject, detect, attribute, and recover from.
Labels: **R** real (hardware/OS genuinely misbehaves), **I** induced (real mechanism,
deliberately triggered), **S** synthetic (fabricated telemetry). Tier: Must / Should / Stretch.

Every exact counter name, XID meaning, and default timeout below must be verified against
the installed driver/NCCL/PyTorch versions and recorded in `docs/ENVIRONMENT.md`. Do not
trust this table over the documentation for your versions.

| ID | Fault | Layer | Injection mechanism | Label | Primary signals | Correct verdict (culprit) | Recovery action | Tier |
|---|---|---|---|---|---|---|---|---|
| F01 | Rank process crash | Process | SIGKILL target rank | R | Agent: process exit; peers later time out | process_crash (rank) | Restart that rank in place, restore tier 0/1; others re-init comms | Must |
| F02 | Stuck rank inside a collective | NCCL | Interposer blocks target rank in `ncclAllReduce` (or chosen op) at step N | I | Progress stalls on all ranks; flight recorder: culprit's last *completed* seq lags / op never entered or never completed | collective_hang (rank) | Abort comms, restart culprit rank, re-init | Must |
| F03 | Stuck rank outside collectives | Process/host | SIGSTOP, or induced infinite loop in dataloader worker | I | Culprit's progress beacon stops first; peers blocked in next collective; FR shows peers ahead | host_hang (rank) | Kill + restart culprit | Must |
| F04 | Collective desync / mismatch | NCCL/app | Interposer issues different op, dtype, or size on one rank | I | FR: mismatched (op, size) at same seq across ranks | collective_desync (rank) | Halt + surface bug (not a hardware fault — never cordon) | Must |
| F05 | GPU straggler: clocks | GPU | Lock target GPU clocks low (`nvidia-smi -lgc`), revert after | I | Per-rank compute time outlier; DCGM clocks/throttle | straggler_gpu (gpu) | Alert → if persistent, replace node/GPU at next checkpoint boundary | Must |
| F06 | GPU straggler: power cap | GPU | Lower power limit on target GPU, revert after | I | Compute-time outlier; DCGM power-cap throttle reason | straggler_gpu (gpu) | Same as F05 | Should |
| F07 | Host straggler | Host | CPU contention pinned to the rank's cores / slowed dataloader | I | Data-wait fraction outlier; host CPU metrics; GPU looks healthy | straggler_host (node) | Alert; do *not* blame GPU | Should |
| F08 | NIC link down | NIC/fabric | `ip link set <roce_netdev> down` or `ibportstate … disable` | R | Port state change; NCCL IB error after local-ack-timeout × retries; `link_downed` | nic_link_down (nic/port) | Cordon/route around; replace node or remap rail; restore | Must |
| F09 | NIC link flapping | NIC/fabric | Repeated down/up with jitter | R | Repeated state changes; symbol/rcv error counters; intermittent retransmits | nic_link_flap (port) | Cordon after N flaps/window; avoid restarting onto it | Must |
| F10 | Fabric congestion / PFC pressure | Fabric | Competing `ib_write_bw` flows through shared links; if switch access allows, provoke PFC | R | Collective time inflation on affected rail; ECN/CNP counters rising; PFC pause counters | fabric_congestion (link/rail) | Alert + attribute; no restart (restart doesn't fix congestion) | Should |
| F11 | NCCL transport error | NCCL | Interposer returns error from a NCCL call / async error | I | `ncclCommGetAsyncError`, PG exception | nccl_transport_error (rank/nic via telemetry join) | Abort + re-init; if correlated with NIC counters → F08/F09 path | Must |
| F12 | GPU hardware fault | GPU | DCGM field injection of XID / ECC values; interposer forcing CUDA error | S / I | XID event (e.g. fallen-off-bus class, DBE/uncontained ECC class, NVLink error class — verify codes), CUDA error on rank | gpu_hw_fault (gpu) | Cordon GPU/node, replace, restore tier 1 | Must (labeled S) |
| F13 | GPU OOM | GPU/app | Allocate ballast on target rank | R | CUDA OOM exception; memory telemetry | gpu_oom (rank) | Restart rank; flag as config issue, don't cordon | Should |
| F14 | Checkpoint storage slow/full | Storage | Throttle or fill checkpoint volume | R | Checkpoint stall time spike; disk latency; write errors | storage_degraded (storage) | Fall back to tier 0/1; alert; skip tier 2 until healthy | Must |
| F15 | Checkpoint corruption | Storage | Flip bytes in a committed shard | I | sha256 mismatch on restore | ckpt_corrupt (shard) | Fall back to previous valid manifest / other tier | Must |
| F16 | Node loss | Node | Kill agent + all ranks on node, or power off (confirmation required) | R | Heartbeat loss for all ranks on node; NIC ports unreachable from peers | node_loss (node) | Replace from spare via placer; restore tier 1 from peer | Must |
| F17 | Silent data corruption | GPU/app | Hook flips bits in a gradient shard on one rank | I | Cross-replica checksum mismatch; grad-norm / loss anomaly | sdc (rank/gpu) | Roll back to pre-anomaly checkpoint; quarantine GPU | Stretch |
| F18 | Controller crash | goodput | Kill controller | R | Lease loss | control_plane_fault | Training continues; controller restarts from event log | Must |

## Gotchas Claude Code must respect (and Naresh must be able to explain)

- **`tc netem` / iptables do not affect RDMA traffic.** RoCE/IB data path bypasses the kernel
  stack. Network impairment on the RDMA path needs port state changes, competing RDMA
  traffic, or switch-side controls. `netem` only works if NCCL is forced onto the Socket
  transport — useful for dev, but label such runs clearly; they are not RDMA results.
- **Time-to-error on link loss is a function of IB transport timeouts.** Local ack timeout
  is 4.096 µs × 2^`NCCL_IB_TIMEOUT`, multiplied by retry count (`NCCL_IB_RETRY_CNT`).
  Record the values in effect; they directly bound detection latency via the NCCL path,
  which is exactly why telemetry-based detection (port state) can beat it.
- **All ranks time out on a hang.** "First rank to report" is not attribution. Use flight
  recorder sequence numbers (who never entered / who is behind) plus progress beacons.
- **Desync is a software bug, not hardware.** Cordoning a node for F04 is a false positive.
- **Stragglers are not failures.** Restarting for a straggler can cost more than it saves;
  policy must weigh remaining time-to-checkpoint against slowdown.
- **Congestion is not a node fault.** Restarting doesn't fix it and moves the problem.
- **Reverts are part of the fault.** Clock locks, power caps, and link-downs must be reverted
  even if the harness crashes (watchdog auto-revert + revert-on-startup sweep).
- **Synthetic XIDs prove the pipeline, not the physics.** Never report detection results on
  S-labeled faults as evidence about real GPU failures.

## Harvesting real faults

Anything the collectors catch that was *not* in the ledger is a candidate real fault.
Store it in `bench/real_faults/` with raw evidence and a manual label; these are the most
valuable records in the dataset and the best interview stories.
