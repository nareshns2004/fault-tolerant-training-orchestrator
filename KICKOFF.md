# Kickoff — how to start goodput with Claude Code

## One-time setup (5 minutes)
1. `mkdir goodput && cd goodput && git init`
2. Copy this bundle in: `CLAUDE.md`, `docs/`, `.claude/commands/`. Keep `KICKOFF.md` out of
   the repo (or delete it after use).
3. Fill the **manual section** of `docs/ENVIRONMENT.md` — at minimum the host allowlist and
   the provenance/clearance line. Claude Code will refuse hardware actions without it.
4. `claude` in the repo root. CLAUDE.md is picked up automatically.
5. Switch to plan mode (Shift+Tab until it shows plan mode) before the first prompt.

## First prompt (paste as-is)

> Read CLAUDE.md, then docs/PROJECT_BRIEF.md, docs/ARCHITECTURE.md, docs/MILESTONES.md and
> docs/EVALUATION.md. Do not write code yet.
>
> 1. Summarize the project back to me in ≤ 15 lines: problem, thesis, the headline metric,
>    and what makes it different from torchrun/torchft/NVRx. I'll correct misunderstandings.
> 2. List every ambiguity, contradiction, or unrealistic target you see across the docs.
>    Be blunt — I want them caught now, not in M4.
> 3. Inspect this machine (read-only commands only): GPUs, driver/CUDA, NCCL and PyTorch
>    availability, RDMA devices and port states, NUMA layout. Report what's present and
>    what's missing for M1.
> 4. Then run /plan-milestone M1 and stop for my approval.

## Session hygiene
- Start each session with: "Read CLAUDE.md and docs/MILESTONES.md; we're on <task>."
- After finishing any component: `/drill <component>`.
- When a decision is made in chat, have Claude Code write the ADR before moving on.
- Use `/clear` between unrelated tasks; the docs carry the context, not the chat history.
