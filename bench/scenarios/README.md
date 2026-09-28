# Experiment scenarios

Each experiment YAML fixes the workload config, the system variant (`goodput`, `B0`,
`B1`, `B2`), the faultlab scenario, the trial count and the seed. `make bench SCENARIO=<file>`
takes one of these files.

The schema is part of M1. It will land together with `bench/runner.py`.
