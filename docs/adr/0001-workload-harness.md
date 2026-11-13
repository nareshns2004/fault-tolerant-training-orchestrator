# ADR-0001: Use torchtitan as the training workload

- Status: Accepted (2026-11-13, ADR-0007); pin the torchtitan commit in M1b

## Context
We need a realistic, modern PyTorch-native LLM training loop (FSDP2, TP, DCP async
checkpointing) without writing a training framework, which is a non-goal.

## Options
1. torchtitan — PyTorch-native, FSDP2/TP/PP, DCP; close to what AI labs run on PyTorch.
2. Megatron-LM — industry-standard, heavier; more NVIDIA-stack coupling.
3. nanoGPT + DDP — simple, but DDP-only is not representative of large-model sharding.

## Decision
torchtitan for primary results; nanoGPT-class model for fast dev loops. Pin a commit.
Revisit if integration hooks prove too invasive.
