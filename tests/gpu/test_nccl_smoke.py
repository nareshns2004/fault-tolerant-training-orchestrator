from __future__ import annotations

import pytest

pytestmark = pytest.mark.gpu


def test_cuda_and_nccl_visible() -> None:
    torch = pytest.importorskip("torch")
    assert torch.cuda.is_available(), "no CUDA device"
    assert torch.cuda.nccl.version() is not None
