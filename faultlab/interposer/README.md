# NCCL/CUDA LD_PRELOAD interposer (C17)

`[OWNER-CORE]` M2: Naresh writes the hang and mismatch logic.

It forces induced faults F02 (hang), F04 (desync) and F11 (error) at a chosen
(rank, step, op). It works by interposing `nccl*` and selected `cuda*` entry points.

## Contract (proposed)

- Configuration comes only from a file path given in `GOODPUT_INTERPOSER_CONFIG`.
  Document it in `docs/ENVIRONMENT.md`. If the file is absent, every call passes through.
- Symbols are resolved with `dlsym(RTLD_NEXT, ...)`. No exceptions or `longjmp` cross the
  C ABI. On any internal error it passes through and logs; the interposer must never be
  the cause of a fault it did not intend.
- Each triggered action appends one JSON line to a file named by the config. faultlab turns
  these lines into `FaultInjection` ledger records.
- Build flags are `-std=c17 -Wall -Wextra -Werror -fPIC`. Debug builds use
  `-fsanitize=address,undefined`.
- Test it on CPU against a fake `libnccl.so` shim so the logic can be checked without GPUs.
