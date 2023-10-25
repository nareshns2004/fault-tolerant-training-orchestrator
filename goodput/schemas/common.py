"""Enumerations and value types shared across schemas."""

from __future__ import annotations

from enum import IntEnum, StrEnum

from pydantic import model_validator

from goodput.schemas._base import SchemaModel


class Provenance(StrEnum):
    """Where a fault or a telemetry value came from (CLAUDE.md rule 4). Never blur these.

    ``real``      hardware/OS genuinely misbehaved (harvested, not scheduled by us).
    ``induced``   a real mechanism, deliberately triggered (SIGKILL, interposer hang,
                  ``ip link set down``).
    ``synthetic`` fabricated values (e.g. DCGM field injection). Proves the pipeline,
                  never the physics.

    For telemetry, the label describes the *value*: a counter genuinely read from
    hardware during an induced fault is ``real``; the fault's own provenance lives on
    the ``FaultInjection``. (Proposed interpretation — see docs/OPEN_QUESTIONS.md OQ-2.)
    """

    REAL = "real"
    INDUCED = "induced"
    SYNTHETIC = "synthetic"


class FaultClass(StrEnum):
    """Verdict vocabulary. One value per 'Correct verdict' in docs/FAULT_MATRIX.md."""

    PROCESS_CRASH = "process_crash"  # F01
    COLLECTIVE_HANG = "collective_hang"  # F02
    HOST_HANG = "host_hang"  # F03
    COLLECTIVE_DESYNC = "collective_desync"  # F04 — software bug; never cordon
    STRAGGLER_GPU = "straggler_gpu"  # F05, F06
    STRAGGLER_HOST = "straggler_host"  # F07
    NIC_LINK_DOWN = "nic_link_down"  # F08
    NIC_LINK_FLAP = "nic_link_flap"  # F09
    FABRIC_CONGESTION = "fabric_congestion"  # F10
    NCCL_TRANSPORT_ERROR = "nccl_transport_error"  # F11
    GPU_HW_FAULT = "gpu_hw_fault"  # F12
    GPU_OOM = "gpu_oom"  # F13
    STORAGE_DEGRADED = "storage_degraded"  # F14
    CKPT_CORRUPT = "ckpt_corrupt"  # F15
    NODE_LOSS = "node_loss"  # F16
    SDC = "sdc"  # F17 (Stretch)
    CONTROL_PLANE_FAULT = "control_plane_fault"  # F18
    UNKNOWN = "unknown"  # classifier abstains; policy must treat as low confidence


class EntityKind(StrEnum):
    GPU = "gpu"
    NIC = "nic"
    PORT = "port"
    NODE = "node"
    DISK = "disk"
    PROCESS = "process"


class Tier(IntEnum):
    """Checkpoint tiers (ARCHITECTURE.md §3.4)."""

    HOST = 0  # pinned host memory, same node; lost with the node
    PEER = 1  # replica on a peer in a different failure domain
    DURABLE = 2  # async DCP to shared storage


class JobState(StrEnum):
    """Controller job states (ARCHITECTURE.md §3.3).

    Only the vocabulary lives here. The transition rules are the recovery state machine,
    which is [OWNER-CORE] (M5) — see goodput/controller/state_machine.py.
    """

    INIT = "INIT"
    RENDEZVOUS = "RENDEZVOUS"
    RUNNING = "RUNNING"
    SUSPECT = "SUSPECT"
    DECIDED = "DECIDED"
    RECOVERING = "RECOVERING"
    ESCALATE = "ESCALATE"


class ComponentRef(SchemaModel):
    """A physical or logical component, at any granularity.

    Used both as a fault *target* (ledger) and a verdict *culprit*, so attribution
    accuracy is a field-by-field comparison of the same type (EVALUATION.md §1).
    Unset fields mean "not asserted", not "healthy".
    """

    node: str | None = None
    rank: int | None = None
    gpu_uuid: str | None = None
    nic: str | None = None  # RDMA device name as discovered, e.g. from ibv_devinfo
    port: int | None = None  # port number on ``nic``
    storage: str | None = None  # mount path or volume id

    @model_validator(mode="after")
    def _port_needs_nic(self) -> ComponentRef:
        if self.port is not None and self.nic is None:
            raise ValueError("port requires nic")
        return self
