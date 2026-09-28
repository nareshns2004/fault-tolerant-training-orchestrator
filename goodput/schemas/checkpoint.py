"""Checkpoint manifest. A checkpoint exists only once its manifest is committed."""

from __future__ import annotations

from typing import Literal

from pydantic import Field, JsonValue, model_validator

from goodput.schemas._base import SchemaModel, UtcNs
from goodput.schemas.common import Tier


class ShardRef(SchemaModel):
    rank: int = Field(ge=0)
    location: str = Field(min_length=1, description="path (tier 0/2) or peer node id (tier 1)")
    bytes: int = Field(ge=0)
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


class MeshLayout(SchemaModel):
    """Enough to decide whether a restore needs resharding (e.g. after elastic shrink)."""

    world_size: int = Field(ge=1)
    dim_names: tuple[str, ...]
    dim_sizes: tuple[int, ...]

    @model_validator(mode="after")
    def _shape(self) -> MeshLayout:
        if len(self.dim_names) != len(self.dim_sizes):
            raise ValueError("dim_names and dim_sizes differ in length")
        prod = 1
        for s in self.dim_sizes:
            prod *= s
        if prod != self.world_size:
            raise ValueError(f"mesh {self.dim_sizes} does not multiply to {self.world_size}")
        return self


class CheckpointManifest(SchemaModel):
    schema_v: Literal[1] = 1
    step: int = Field(ge=0)
    tier: Tier
    shards: tuple[ShardRef, ...] = Field(min_length=1)
    mesh: MeshLayout
    dataloader_state: dict[str, JsonValue]
    rng_state_ref: str = Field(min_length=1, description="location of serialized RNG state")
    committed_at_utc_ns: UtcNs

    @model_validator(mode="after")
    def _complete(self) -> CheckpointManifest:
        ranks = sorted(s.rank for s in self.shards)
        if ranks != list(range(self.mesh.world_size)):
            raise ValueError("manifest must hold exactly one shard per rank in the mesh")
        return self
