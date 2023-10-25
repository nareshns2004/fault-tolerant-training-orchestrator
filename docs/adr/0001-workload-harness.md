# ADR-0001: Use torchtitan as the training workload

- Status: Proposed

## Context
We need a realistic, modern PyTorch-native LLM training loop (FSDP2, TP, DCP async
checkpointing) without writing a training framework, which is a non-goal.

## Options
1. torchtitan — PyTorch-native, FSDP2/TP/PP, DCP; close to what AI labs run on PyTorch.
2. Megatron-LM — industry-standard, heavier; more NVIDIA-stack coupling.
3. nanoGPT + DDP — simple, but DDP-only is not representative of large-model sharding.

## Leaning
torchtitan for primary results; nanoGPT-class model for fast dev loops. Pin a commit.
Revisit if integration hooks prove too invasive.
