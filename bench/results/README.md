# Results

Each run is stored in `bench/results/<run_id>/`, laid out as in docs/EVALUATION.md §5:

```
<run_id>/
  config.yaml         # exact experiment config
  env_manifest.json   # GPU, driver, CUDA, NCCL, PyTorch, torchtitan commit, NIC + fw,
                      # kernel, rdma-core, relevant env vars, topology.json hash
  events.jsonl        # goodput event log            (gitignored: raw)
  ledger.jsonl        # faultlab ground truth        (gitignored: raw)
  telemetry/          # extracts                     (gitignored: raw)
  summary/            # generated tables + plots     (committed)
```

Only `summary/` is committed. Any number in a README, blog post, doc or commit message
must link to a `<run_id>` here (CLAUDE.md rule 3).
