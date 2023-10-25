# Architecture — goodput

Status: initial design. Anything marked *(ADR)* is a decision to be ratified in `docs/adr/`.

## 1. Design principles

1. **Out of the data path.** The controller never sits between ranks and their collectives.
   If every goodput component dies, training continues exactly as stock PyTorch would.
2. **Attribution before action.** No recovery action is taken without a Verdict that carries
   evidence. "Restart everything" is an explicit, logged fallback, not the default.
3. **Topology is a first-class input.** Every rank maps to (node, GPU UUID, PCIe/NUMA,
   NIC/port, rail, leaf switch, rack). Policy and checkpoint placement reason over it.
4. **Everything is an event.** Faults, telemetry anomalies, verdicts, actions, and phase
   transitions are timestamped, schema-versioned events. Evaluation is computed from the
   event log, never from ad-hoc timers.
5. **Cheap in steady state.** Rank-side hooks are O(1) per step; heavy analysis only runs
   after a trigger.

## 2. System context

```
                 ┌──────────────────────── controller (1 per job) ────────────────────────┐
                 │  membership/state machine · correlator · classifier · policy · placer  │
                 │  event log (append-only) · checkpoint catalog · metrics endpoint       │
                 └───────▲──────────────────────────▲─────────────────────────┬───────────┘
          heartbeats,    │                          │ telemetry anomalies,    │ actions
          progress,      │                          │ kernel-log events       │ (abort comm,
          FR dumps       │                          │                         │  restart, cordon,
 ┌───────── node N ──────┴──────────────────────────┴─────┐                   │  restore, shrink)
 │  node agent: supervises local ranks · collectors:       │◄──────────────────┘
 │  DCGM · RDMA counters (sysfs/hw_counters, ethtool -S)   │
 │  · kernel log (XID, mlx5, PCIe AER) · host (CPU, mem)   │
 │  · checkpoint tier-0/1 buffers (pinned host memory)     │
 │   ┌── rank 0 ──┐ ┌── rank 1 ──┐ … ┌── rank 7 ──┐        │
 │   │ torchtitan │ │            │   │            │        │   faultlab (separate CLI/daemon)
 │   │ + goodput  │ │            │   │            │        │◄── injects faults, writes ledger
 │   │   hooks    │ │            │   │            │        │
 └───┴────────────┴─┴────────────┴───┴────────────┴────────┘
```

## 3. Components

### 3.1 Rank-side hooks (`goodput/rank/`) — in-process, minimal
- Progress beacon: step counter + monotonic timestamp, pushed to local agent every step via
  shared memory or a Unix socket (never a network call on the hot path).
- Step timing split (data wait, forward/backward, optimizer, checkpoint stall) using CUDA
  events; used for straggler detection.
- Collective tracking: rely on ProcessGroupNCCL flight recorder (enable trace buffer and
  dump-on-timeout); the hook only guarantees dumps are written to a known path and that a
  dump can be requested on demand from the agent.
- Recovery entry points: `abort_and_reinit_comms()`, `restore(from=tier)`,
  `rebuild_mesh(world)`. In-process restart must be designed with the realities of a
  poisoned NCCL communicator and possibly bad CUDA context state in mind *(ADR)*.
- Sample ledger: records (step, rank, sample ids) for correctness verification.

### 3.2 Node agent (`goodput/agent/`)
- Launches/supervises local ranks (wraps or replaces torchrun's local agent *(ADR)*).
- Liveness: process state, heartbeat freshness, progress freshness (distinguish *dead*,
  *hung*, *slow*).
- Collectors, all emitting normalized `TelemetrySample`/`Event`:
  - GPU: DCGM (XID events, ECC SBE/DBE, row remap, NVLink CRC/replay, PCIe replay,
    throttle reasons, clocks, power, temperature, utilization).
  - NIC/fabric: `/sys/class/infiniband/<dev>/ports/<p>/{state,phys_state,counters,hw_counters}`
    (e.g. link_downed, symbol_error, port_rcv_errors, out_of_sequence, packet_seq_err,
    local_ack_timeout_err, rnr_nak_retry_err, ECN/CNP counters — exact names are
    driver-specific; discover, don't hardcode) and `ethtool -S` for per-priority PFC pause.
  - Kernel log: XID lines, mlx5 errors, PCIe AER, OOM killer.
  - Host: CPU steal/throttle, memory pressure, disk latency on checkpoint volume.
- Change-point/threshold detection locally; ships anomalies, not raw firehose, to the
  controller. Raw series go to Prometheus for dashboards.

### 3.3 Controller (`goodput/controller/`)
- Job state machine:

```
 INIT → RENDEZVOUS → RUNNING ──trigger──► SUSPECT ──verdict──► DECIDED ──► RECOVERING ──► RUNNING
                        ▲          │                     │                    │
                        │          └─(cleared)───────────┘                    ├─fail→ ESCALATE
                        └──────────────────────────────────────────────────────┘   (wider blast
                                                                                    radius or halt)
```
  Every transition is an event with timestamp; MTTD/MTTR phases are computed from these.
- Correlator: on trigger, gathers a window (default ±N s, configurable) of events from all
  agents, joins on topology (rank → GPU → NIC → switch), and builds an `Incident`.
- Classifier: `Classifier` interface. v1 = deterministic rules over `Incident` features
  (flight-recorder seq analysis, telemetry anomalies, liveness). v2 = model from the HF
  project behind the same interface, evaluated on the same held-out set.
- Policy engine: `Verdict → Action` table (see FAULT_MATRIX), with guards: max restarts
  per window, spare-capacity check, escalation ladder.
- Placer: chooses replacement nodes and checkpoint-replica peers using the topology model
  and failure-domain constraints.
- Membership/rendezvous backend *(ADR)*: reuse c10d store / etcd rather than invent.

### 3.4 Checkpoint manager (`goodput/ckpt/`)
- Tier 0: snapshot of sharded state to pinned host memory on the same node (fast, lost with
  the node).
- Tier 1: replica of each node's tier-0 shard on a *peer* node chosen by the placer to be in
  a different failure domain (different rack/leaf/PSU where known) but with good bandwidth.
  Transport v1: separate process group; Stretch: raw verbs replicator *(ADR)*.
- Tier 2: durable async DCP save to shared storage, less frequent.
- Atomic commit: a checkpoint is valid only when its manifest (step, shard list, checksums,
  world/mesh layout, dataloader + RNG state) is committed; readers ignore incomplete sets.
- Restore-path selection per fault: local tier 0 (process crash), peer tier 1 (node loss),
  tier 2 (correlated failure / corruption detected).
- Interval selection: start from Young/Daly with measured checkpoint cost and observed MTBF;
  expose as config.

### 3.5 Topology (`goodput/topology/`)
- Discovery: `nvidia-smi topo -m`, NVML, `ibv_devinfo`, `lspci -tv`, NUMA from sysfs,
  optional LLDP for NIC→switch-port mapping, rail assignment.
- Output: `artifacts/topology.json` (graph: nodes, edges with bandwidth class, failure
  domains). Used by correlator, placer, and reports.

### 3.6 faultlab (`faultlab/`)
- Declarative scenario YAML: fault id, target selector (rank/gpu/nic/node), trigger (step,
  wall time, Poisson schedule), duration, revert.
- Mechanisms: signals to processes; LD_PRELOAD interposer (C) around NCCL/CUDA entry points
  to force hangs, errors, or collective mismatch at a chosen (rank, step, op); nvidia-smi
  clock/power limits; `ip link` / `ibportstate`; competing `ib_write_bw` traffic; storage
  throttling; DCGM field injection (synthetic only).
- Ground-truth ledger: every injection writes `FaultInjection` records (start, end, target,
  mechanism, label real/induced/synthetic). Revert is registered before injection;
  watchdog auto-reverts on timeout or controller exit.

### 3.7 bench / sim / export
- `bench/`: experiment runner → `bench/results/<run_id>/` (raw event log, telemetry,
  env manifest, config) → report generator.
- `sim/`: discrete-event goodput simulator parameterized by measured phase distributions
  and literature failure rates; outputs projected goodput vs scale and checkpoint interval.
- `export/`: builds the HF dataset (see §5) from ledgers + incidents.

## 4. Core schemas (`goodput/schemas/`, versioned)

The source of truth is the pydantic models. This section is a summary. Every model carries
`schema_v` (currently `1`), is frozen, and rejects unknown fields. `*_utc_ns` is used to
correlate across hosts; `*_mono_ns` is for durations on one host only.

- `Event {schema_v, event_id, ts_utc_ns, ts_mono_ns, source, node, rank?, kind, payload}`.
  `kind` is a dotted namespace (e.g. `state.transition`).
- `TelemetrySample {schema_v, ts_utc_ns, node, metric, entity(gpu|nic|port|node|disk|process),
   entity_id, value, unit, provenance(real|induced|synthetic)}`
- `ComponentRef {node?, rank?, gpu_uuid?, nic?, port?, storage?}`. Used as both the fault
  target and the verdict culprit, so attribution accuracy compares like with like.
- `FaultInjection {schema_v, id, fault_id(Fnn), fault_class, label(real|induced|synthetic),
   target: ComponentRef, mechanism, scenario_id?, t_start_utc_ns, t_end_utc_ns?, revert_ok?}`
- `Incident {schema_v, id, trigger_event, window_start/end_utc_ns, events[], topology_slice}`
- `Verdict {schema_v, incident_id, fault_class, culprit: ComponentRef, confidence[0,1],
   evidence[event_id], classifier_version}`. Evidence is required unless the class is
  `unknown`.
- `Action {schema_v, id, verdict_id, kind(reinit_comm|restart_ranks|replace_node|shrink|
   rollback|halt), targets[ComponentRef], restore_tier?, started/finished_utc_ns?, outcome}`
- `CheckpointManifest {schema_v, step, tier, shards[{rank, location, bytes, sha256}],
   mesh{world_size, dim_names, dim_sizes}, dataloader_state, rng_state_ref,
   committed_at_utc_ns}`. A manifest must hold exactly one shard per rank.
- `Topology {schema_v, hosts[{hostname, gpus, nics(ports), domain{rack, leaf, psu}}],
   ranks[{rank, hostname, gpu_uuid?, nic?, port?}]}`

Changes from the initial design: `event_id` (needed for `Verdict.evidence`);
`ts_utc_ns`, `node` and `provenance` on `TelemetrySample` (rule 4 labels every sample);
the shared `ComponentRef`; `fault_id` and `scenario_id` on `FaultInjection`; and
`rng_state_ref` instead of inline RNG state.

## 5. Dataset export (feeds Hugging Face projects)

One record per incident: normalized, time-ordered event text + structured features,
ground-truth fault class and culprit from the ledger, the rules verdict, label provenance
(real/induced/synthetic), and hardware context. Splits by *scenario seed and node*, not by
random record, to avoid leakage. Dataset card documents provenance and limitations.

## 6. Failure semantics of goodput itself

- Controller crash: training continues; agents buffer events and fall back to a local
  conservative policy (restart local ranks only on confirmed local process death).
- Agent crash: ranks continue; controller marks node telemetry-blind and lowers confidence
  on verdicts involving it.
- Split-brain avoidance: only the controller holding the job lease may issue cluster-wide
  actions *(ADR)*.

## 7. Scaling notes (for interviews; not all implemented)

Fan-in: agents send anomalies, not raw series; hierarchical aggregation (per-rack) beyond
~1K nodes. Heartbeat intervals and timeouts are tuned against false-positive cost.
Flight-recorder analysis is O(ranks × buffer) and runs only on trigger. Correlation window
and topology join are bounded by the affected communicator, not the whole cluster.

## 8. Repo layout

See ADR-0004 for the package boundaries. `goodput` never imports `faultlab` or `bench`, and
`faultlab` imports only `goodput.schemas`. A test enforces both rules.

```
goodput/            # system under test (python package)
  schemas/ rank/ agent/ controller/ ckpt/ topology/ signals/ policy/ sim/ export/
faultlab/           # adversary + ground truth (python package)
  mechanisms/ scenarios/ interposer/ (C) ledger.py safety.py
bench/              # evaluator (python package): runner, metrics, reports
  scenarios/ results/ (raw gitignored; summary/ committed)
configs/            # example configs; real host lists are *.local.yaml (gitignored)
dashboards/         # Grafana JSON
docs/               # this folder
tests/              # unit/, integration/ (gloo, CPU), gpu/, multinode/, fixtures/
```
