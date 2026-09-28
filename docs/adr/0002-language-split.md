# ADR-0002: Language split

- Status: Proposed

## Leaning
- Python (asyncio, gRPC or plain HTTP/JSON *(decide)*) for agent, controller, signals,
  policy, bench — speed of iteration, direct access to PyTorch internals.
- C for the LD_PRELOAD NCCL/CUDA interposer — must be C ABI.
- C++ only where it earns it (Stretch: raw-verbs checkpoint replicator, possibly shared
  with the inference repo's RDMA transport via pybind11).
Revisit if agent overhead or event throughput measurements demand it.
