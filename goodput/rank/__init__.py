"""Rank-side hooks: in-process, O(1) per step, never a network call on the hot path.

See ARCHITECTURE.md §3.1. Anything importing ``torch`` lives here or in ``goodput.ckpt``
and is imported lazily, so the controller stays importable without torch.
"""
