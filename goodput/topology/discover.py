"""Topology discovery -> ``artifacts/topology.json`` (``make topo``, M1).

Sources, all read-only: NVML / ``nvidia-smi topo -m``, ``/sys/class/infiniband``,
``ibv_devinfo``, ``lspci -tv``, ``/sys/devices/system/node``, optional LLDP.
Must run unprivileged and degrade to ``None`` fields when a source is missing.
"""

from __future__ import annotations

from goodput.schemas import Topology


def discover_local() -> Topology:
    """Discover this host's GPUs, NICs, and NUMA placement."""
    raise NotImplementedError("M1: topology discovery")
