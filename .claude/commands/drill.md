---
description: Interview drill on the component just finished; grade answers against the artifacts
argument-hint: [component, e.g. "faultlab ledger"; default = the last thing changed]
---

Run a defence drill on **$ARGUMENTS** (if empty, use the component touched by the most
recent commits: `git log -5 --stat`).

1. Read the component's code, tests, and the docs that justify it: the relevant
   `docs/ARCHITECTURE.md` section, its ADRs (especially "Options considered"),
   `docs/EVALUATION.md` for any metric it feeds, and `docs/prior_art.md` for anything it
   reuses or competes with.
2. Ask **5 questions, one at a time**, the way a skeptical senior interviewer would:
   - 1 on mechanism (how it works, down to the syscall, verb or NCCL call where relevant),
   - 1 on a rejected alternative (why not the option the ADR rejected),
   - 1 on failure (what breaks it, what happens when it is itself faulted),
   - 1 on measurement (how we know the number is real: sample size, baseline, provenance),
   - 1 on prior art (what NVRx / torchft / the flight recorder already does here).
3. After each answer, grade it **against the repo, not general knowledge**: correct /
   partially correct / wrong, cite the file and line or doc section that settles it, and
   give the one-sentence answer the repo supports. If the repo itself cannot answer the
   question, say so: that is a documentation gap, so propose where it should be written.
4. Finish with a score out of 5 and the list of gaps. Do not edit files unless asked.
