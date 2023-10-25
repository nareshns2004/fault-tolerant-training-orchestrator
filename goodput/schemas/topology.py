"""Topology model: rank -> GPU -> NUMA -> NIC/port -> rail -> switch (ARCHITECTURE §3.5).

Serialized to ``artifacts/topology.json`` by ``make topo``. Fields that cannot be
discovered on a given cluster (e.g. leaf switch without LLDP) stay ``None``; consumers
must treat ``None`` as unknown, never as "same" or "different".
"""

from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import Field, model_validator

from goodput.schemas._base import SchemaModel


class LinkLayer(StrEnum):
    INFINIBAND = "InfiniBand"
    ETHERNET = "Ethernet"  # RoCE


class Gpu(SchemaModel):
    index: int = Field(ge=0)
    uuid: str
    pci_bus_id: str
    numa_node: int | None = None


class NicPort(SchemaModel):
    device: str  # e.g. as listed under /sys/class/infiniband
    port: int = Field(ge=1)
    netdev: str | None = None
    link_layer: LinkLayer
    numa_node: int | None = None
    rail: int | None = None
    switch: str | None = None
    switch_port: str | None = None


class FailureDomain(SchemaModel):
    rack: str | None = None
    leaf: str | None = None
    psu: str | None = None


class Host(SchemaModel):
    hostname: str
    gpus: tuple[Gpu, ...] = ()
    nics: tuple[NicPort, ...] = ()
    domain: FailureDomain = FailureDomain()


class RankPlacement(SchemaModel):
    rank: int = Field(ge=0)
    hostname: str
    gpu_uuid: str | None = None
    nic: str | None = None
    port: int | None = None


class Topology(SchemaModel):
    schema_v: Literal[1] = 1
    hosts: tuple[Host, ...]
    ranks: tuple[RankPlacement, ...] = ()

    @model_validator(mode="after")
    def _ranks_on_known_hosts(self) -> Topology:
        names = {h.hostname for h in self.hosts}
        for r in self.ranks:
            if r.hostname not in names:
                raise ValueError(f"rank {r.rank} placed on unknown host {r.hostname!r}")
        if len({r.rank for r in self.ranks}) != len(self.ranks):
            raise ValueError("duplicate rank in placement")
        return self
