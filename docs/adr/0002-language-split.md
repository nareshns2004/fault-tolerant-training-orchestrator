# ADR-0002: Language split and control-plane transport

- Status: Accepted (2026-11-13; transport decided in ADR-0007, OQ-18)

## Decision
- Python (asyncio) for agent, controller, signals, policy, bench: speed of iteration and
  direct access to PyTorch internals. Control-plane messages are **HTTP/JSON** carrying the
  existing pydantic schemas; gRPC was rejected because it adds a second schema language.
- Rendezvous and membership use the c10d `TCPStore`; the controller lease is a key in that
  store (ADR-0007). etcd is the upgrade path if the store host proves a single point of
  failure.
- C for the LD_PRELOAD NCCL/CUDA interposer, which must be C ABI.
- C++ only where it earns it (Stretch: raw-verbs checkpoint replicator, possibly shared
  with kvwire's RDMA transport via pybind11).

Revisit if agent overhead or event throughput measurements demand it.
