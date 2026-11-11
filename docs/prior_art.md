# Prior art: what exists, what it covers, what goodput reuses

Status: **draft (M1a)**. Each entry records: mechanism, what it covers, what it leaves open,
and what goodput reuses. Claims about other projects cite a source and the version or date
checked. Entries marked *to verify* are taken from the project brief and have not yet been
checked against the primary source.

The gap analysis and the go / re-scope decision at the end are `[OWNER-CORE]`
(MILESTONES M1a).

---

## NVIDIA Resiliency Extension (NVRx)

*Checked 2026-11-11 against the NVRx release notes (v0.5.0 to v0.7.0).*

- **Mechanism / coverage:** fault-tolerance launcher with hang detection and in-job
  restart; in-process restart; async and local checkpointing; straggler detection; health
  checks (NVML-based GPU, NVLink including a windowed replay/recovery-counter check, **NIC
  link state**, distributed storage).
- **Attribution module (experimental in v0.6 and v0.7; APIs may change):**
  - Flight-recorder analysis to identify ranks interrupting progress on a hang or watchdog
    timeout (v0.5.0 onward; window-based ordering in v0.6.0).
  - LLM-based log analysis (LogSage; source-checkout-only from v0.7.0).
  - An attribution service (`attrsvc`) and, in v0.7.0, a Restart Agent with deterministic
    failure evidence and retry policy. Attribution runs asynchronously and does not delay
    restart; acting on a STOP verdict is opt-in.
- **Not found in the release notes:** analysis of RDMA/InfiniBand port or `hw_counters`
  (retransmits, timeouts, ECN/CNP, PFC), or a rank → GPU → NIC → port → switch topology
  join used for attribution. Topology appears only in scheduling (NVLink domains via GPU
  ClusterUUID).
- **Also noted (NeMo docs, to verify):** in-process restart is not suited to switch
  failures or network partitions.
- **Implication for goodput:** culprit-*rank* attribution from the flight recorder is prior
  art. goodput should reuse or wrap it, or use it as the comparison baseline for metric #3
  (EVALUATION §2, B2), instead of claiming it. The remaining candidate gap is
  component-level attribution through fabric counters and topology, and the policy built on
  it. **Before closing the gate, read `src/nvidia_resiliency_ext/attribution` and the
  `attrsvc` spec at the pinned version**: the release notes may not list every input.

Sources: [NVRx release notes](https://nvidia.github.io/nvidia-resiliency-ext/release-notes.html),
[NVRx attribution feature docs](https://nvidia.github.io/nvidia-resiliency-ext/_sources/attribution/features/index.rst.txt).

## PyTorch ProcessGroupNCCL watchdog and flight recorder

- **Covers:** collective timeouts; per-rank ring buffer of recent collectives, dumped on
  timeout or on demand.
- **Leaves open:** cross-rank analysis joined with hardware telemetry.
- **Reuse:** the collective-history source for M3. Dump format is version-specific; record
  the PyTorch version per fixture. *To verify at the pinned version.*

## torchrun / TorchElastic

- **Covers:** rendezvous, restart on worker failure, elastic membership.
- **Leaves open:** why and where it failed; avoiding restarts onto bad hardware.
- **Reuse:** B0 baseline; possibly the rendezvous backend. *To verify.*

## PyTorch DCP (including async save)

- **Covers:** sharded, reshardable checkpoints.
- **Leaves open:** tier placement by failure domain; restore path chosen per fault class.
- **Reuse:** tier 2 and resharding. *To verify.*

## torchft

- **Covers:** per-step fault tolerance across replica groups (DDP, HSDP), live peer
  recovery; integrated in torchtitan.
- **Leaves open:** attribution and fabric-layer signals. Complementary. *To verify.*

## DCGM / dcgm-exporter

- **Covers:** GPU health fields, XIDs, diagnostics, field injection for testing.
- **Leaves open:** correlation with training symptoms and rank mapping.
- **Reuse:** GPU collector; synthetic F12 injection (labelled `synthetic`). *To verify.*

## Published systems and papers

| Work | Mechanism | Relevance | Status |
|---|---|---|---|
| Meta, *The Llama 3 Herd of Models* (2024), §3.3.4, Table 5 | Interruption breakdown for 405B pretraining (419 unexpected in 54 days on 16,384 H100s) | Problem statement, MTBF anchor | *to verify against the paper* |
| Meta, *Revisiting Reliability in Large-Scale ML Research Clusters* (2024) | ETTR definition; failure rate vs job size | Metric comparability | *to verify* |
| ByteDance, *MegaScale* (NSDI '24) | Heartbeats, diagnostics, fast checkpoint/recovery at 10K+ GPUs | Published design, not reusable code | *to verify* |
| GEMINI (SOSP '23) | In-memory checkpoints replicated to peers | Tier-1 design | *to verify* |
| CheckFreq (FAST '21), Check-N-Run (NSDI '22) | Checkpoint frequency and cost | Interval selection | *to verify* |
| Young (1974), Daly (2006) | Optimal checkpoint interval | Baseline tuning | standard result |

---

## Gap analysis and gate decision

`[OWNER-CORE]`: to be written by a maintainer once the entries above are verified.

- Claimed gap, restated against NVRx attribution:
- Evidence:
- Decision (go / re-scope), date:
