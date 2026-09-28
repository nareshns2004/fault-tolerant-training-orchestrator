# Interview Defense — questions this repo must survive

Use with `/drill`. For each: the answer must reference a specific artifact (file, run id,
plot) in this repo. "What a strong answer contains" is a checklist, not a script.

## Problem framing
1. Why is this a real problem? → failure rates at scale from primary sources; how
   interruption cost scales with job size; goodput vs MFU distinction.
2. Why not just use torchrun / torchft / NVRx? → prior_art.md table; the fabric-attribution
   gap; what you reused and why.
3. What's the single number that proves this works? → goodput delta vs B0/B1 on the same
   fault schedule, with MTTR decomposition explaining *where* the gain came from.

## Detection and attribution
4. A 512-rank job hangs; every rank times out. How do you find the bad one? → flight
   recorder seq alignment (never entered / never completed / diverged) + progress beacons
   + telemetry join; why "first to report" is wrong.
5. How do you distinguish hang, desync, straggler, and crash? → signatures.md.
6. What does async error handling do in ProcessGroupNCCL and why abort the communicator
   rather than just raising? → communicator state after an error; why a process may still
   need to exit; CUDA context considerations.
7. Why can telemetry beat NCCL's own error path on a link-down? → IB local-ack timeout
   formula × retry count vs port-state event latency; measured numbers.
8. What's your false-positive story? → FP metric, thresholds, escalation ladder, the cost
   model for a wrong cordon.
9. How do you detect stragglers without adding overhead? → CUDA-event step decomposition,
   robust stats, overhead measurement with CI.
10. Congestion vs broken link vs slow GPU — how do the counters differ? → ECN/CNP, PFC
    pause, symbol/rcv errors, link_downed, DCGM throttle reasons; why restart doesn't fix
    congestion.

## Recovery and checkpointing
11. Walk me through MTTR phase by phase. Which dominates and why? → decomposition plot;
    the re-init hypothesis result.
12. How is a checkpoint made consistent with async saves? → manifest commit, checksums,
    what happens on crash mid-save.
13. Where do you put the peer replica and why? → failure domains vs bandwidth trade-off;
    what correlated failure breaks it.
14. How do you pick checkpoint interval? → Young/Daly, measured C, sensitivity plot.
15. After recovery, how do you prove training is still correct? → sample ledger, loss
    comparison tolerance, optimizer/RNG state checks.
16. You shrink from 16 to 12 GPUs. What changes? → global batch via grad accumulation,
    resharding via DCP, LR schedule, numerics, throughput.
17. When is in-process restart unsafe? → documented class list and why.

## Systems design at scale
18. Scale this to 10K GPUs. What breaks first? → controller fan-in, heartbeat storms,
    event volume, FR analysis cost, hierarchical aggregation.
19. What if the controller dies? Split brain? → out-of-data-path design, lease.
20. What are the clock-sync assumptions for correlation and what happens if they fail?
21. How would this integrate with Slurm or Kubernetes (JobSet/Kueue) in production?

## Fault injection and methodology
22. Why doesn't `tc netem` work for your RDMA faults? → kernel bypass.
23. Which of your faults are real vs induced vs synthetic, and what can you claim from each?
24. How many trials, what confidence intervals, how did you avoid comparing single runs?
25. How do you know the baseline wasn't a strawman? → Young/Daly-tuned interval, async
    DCP, NVRx comparison.

## Data and ML bridge
26. How was the HF dataset built, and how did you prevent leakage between train/test?
27. Why rules first, model second? When does the model beat rules, and how did you measure?

## Honest limitations (say these before being asked)
- Scale: tens of GPUs, not thousands; projections are simulator output, labeled as such.
- GPU hardware faults are synthetic in telemetry; physics not tested.
- Fault mix and MTBF are compressed and chosen, not observed.
- Where goodput lost to a baseline, and why.
