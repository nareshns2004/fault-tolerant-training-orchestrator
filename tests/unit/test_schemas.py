from __future__ import annotations

import pytest
from pydantic import ValidationError

from goodput.schemas import (
    Action,
    ActionKind,
    ActionOutcome,
    CheckpointManifest,
    ComponentRef,
    Event,
    FaultClass,
    FaultInjection,
    MeshLayout,
    Provenance,
    ShardRef,
    Tier,
    Topology,
    Verdict,
)
from goodput.schemas.topology import Host, RankPlacement

SHA = "0" * 64


def _event(**kw: object) -> Event:
    base: dict[str, object] = dict(
        ts_utc_ns=1, ts_mono_ns=1, source="agent", node="n0", kind="state.transition"
    )
    base.update(kw)
    return Event.model_validate(base)


def test_event_roundtrip() -> None:
    e = _event(rank=3, payload={"from": "RUNNING", "to": "SUSPECT"})
    assert Event.model_validate_json(e.model_dump_json()) == e


def test_event_rejects_unknown_fields_and_bad_kind() -> None:
    with pytest.raises(ValidationError):
        _event(surprise=1)
    with pytest.raises(ValidationError):
        _event(kind="NotDotted")


def test_schema_version_is_pinned() -> None:
    with pytest.raises(ValidationError):
        _event(schema_v=2)


def test_models_are_frozen() -> None:
    e = _event()
    with pytest.raises(ValidationError):
        e.node = "other"  # type: ignore[misc]


def test_provenance_values_are_exactly_the_three_labels() -> None:
    assert {p.value for p in Provenance} == {"real", "induced", "synthetic"}


def test_fault_injection_rules() -> None:
    ok = FaultInjection(
        id="x",
        fault_id="F01",
        fault_class=FaultClass.PROCESS_CRASH,
        label=Provenance.INDUCED,
        target=ComponentRef(rank=2),
        mechanism="sigkill",
        t_start_utc_ns=10,
        t_end_utc_ns=20,
    )
    assert ok.fault_id == "F01"
    with pytest.raises(ValidationError, match="precedes"):
        FaultInjection.model_validate(ok.model_dump() | {"t_end_utc_ns": 5})
    with pytest.raises(ValidationError, match="unknown"):
        FaultInjection.model_validate(ok.model_dump() | {"fault_class": "unknown"})
    with pytest.raises(ValidationError):
        FaultInjection.model_validate(ok.model_dump() | {"fault_id": "1"})


def test_port_requires_nic() -> None:
    with pytest.raises(ValidationError, match="port requires nic"):
        ComponentRef(port=1)


def test_verdict_requires_evidence_unless_unknown() -> None:
    kw: dict[str, object] = dict(
        incident_id="i", culprit=ComponentRef(rank=1), confidence=0.9, classifier_version="r1"
    )
    Verdict.model_validate(kw | {"fault_class": "unknown", "evidence": ()})
    with pytest.raises(ValidationError, match="evidence"):
        Verdict.model_validate(kw | {"fault_class": "collective_hang", "evidence": ()})
    with pytest.raises(ValidationError):
        Verdict.model_validate(kw | {"fault_class": "unknown", "evidence": (), "confidence": 1.5})


def test_action_terminal_outcome_needs_timestamps() -> None:
    kw: dict[str, object] = dict(id="a", verdict_id="v", kind=ActionKind.REINIT_COMM, targets=())
    Action.model_validate(kw)
    with pytest.raises(ValidationError):
        Action.model_validate(kw | {"outcome": ActionOutcome.SUCCEEDED})
    with pytest.raises(ValidationError):
        Action.model_validate(kw | {"started_utc_ns": 5, "finished_utc_ns": 4})


def test_manifest_needs_one_shard_per_rank() -> None:
    mesh = MeshLayout(world_size=2, dim_names=("dp",), dim_sizes=(2,))
    shards = (ShardRef(rank=0, location="/a", bytes=1, sha256=SHA),)
    with pytest.raises(ValidationError, match="one shard per rank"):
        CheckpointManifest(
            step=1,
            tier=Tier.HOST,
            shards=shards,
            mesh=mesh,
            dataloader_state={},
            rng_state_ref="/r",
            committed_at_utc_ns=1,
        )


def test_mesh_shape_must_match_world() -> None:
    with pytest.raises(ValidationError):
        MeshLayout(world_size=8, dim_names=("dp", "tp"), dim_sizes=(2, 2))


def test_topology_rejects_rank_on_unknown_host() -> None:
    with pytest.raises(ValidationError, match="unknown host"):
        Topology(hosts=(Host(hostname="a"),), ranks=(RankPlacement(rank=0, hostname="b"),))
