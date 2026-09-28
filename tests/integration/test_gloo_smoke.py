"""Pattern for CPU multi-process tests with the gloo backend (CLAUDE.md rule 9).

Skipped when torch is not installed, so the core suite runs on a bare laptop.
"""

from __future__ import annotations

import pytest

torch = pytest.importorskip("torch")
dist = pytest.importorskip("torch.distributed")
mp = pytest.importorskip("torch.multiprocessing")


def _worker(rank: int, world: int, port: int) -> None:
    dist.init_process_group(
        "gloo", init_method=f"tcp://127.0.0.1:{port}", rank=rank, world_size=world
    )
    t = torch.ones(1) * rank
    dist.all_reduce(t)
    assert t.item() == sum(range(world))
    dist.destroy_process_group()


def test_gloo_allreduce() -> None:
    import socket

    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    mp.spawn(_worker, args=(2, port), nprocs=2, join=True)
