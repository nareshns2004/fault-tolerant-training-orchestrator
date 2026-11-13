from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from bench.export.record import IncidentRecord, render_event_line
from bench.export.schema import SCHEMA_PATH, render
from goodput.schemas import Event


def _record(**overrides: object) -> dict[str, object]:
    base: dict[str, object] = {
        "record_id": "r1",
        "incident_id": "i1",
        "events": [
            {"ref": "e1", "ts_utc_ns": 10, "text": "fabric.port_state nic=mlx5_0 state=down"},
            {"ref": "e2", "ts_utc_ns": 20, "text": "nccl.timeout op=allreduce seq=41"},
        ],
        "labels": {
            "fault_id": "F08",
            "fault_class": "nic_link_down",
            "culprit": {"node": "n1", "nic": "mlx5_0", "port": 1},
        },
        "system_verdict": {
            "incident_id": "i1",
            "fault_class": "nic_link_down",
            "culprit": {"node": "n1", "nic": "mlx5_0", "port": 1},
            "confidence": 0.9,
            "evidence": ["e1"],
            "classifier_version": "rules-0",
        },
        "provenance": "induced",
        "hardware": {
            "num_nodes": 2,
            "gpus_per_node": 8,
            "gpu_model": "H100-SXM",
            "nic_model": "ConnectX-7",
            "fabric": "roce",
            "torch_version": "2.6",
            "nccl_version": "2.25",
            "cuda_version": "12.8",
        },
        "split_keys": {
            "run_id": "run-1",
            "seed": 7,
            "topology_group": "2x8",
            "fault_family": "NIC/fabric",
        },
    }
    base.update(overrides)
    return base


def test_committed_json_schema_matches_models() -> None:
    assert SCHEMA_PATH.exists(), "run `make schemas`"
    assert SCHEMA_PATH.read_text(encoding="utf-8") == render(), (
        "docs/schemas/incident.schema.json is stale: run `make schemas` and bump "
        "RECORD_SCHEMA_V if the change is breaking"
    )
    assert json.loads(render())["x-schema-version"] == 1


def test_valid_record_roundtrips() -> None:
    r = IncidentRecord.model_validate(_record())
    assert IncidentRecord.model_validate_json(r.model_dump_json()) == r


def test_render_event_line_is_deterministic() -> None:
    e = Event(
        ts_utc_ns=1,
        ts_mono_ns=1,
        source="agent/nic",
        node="n0",
        kind="fabric.port_state",
        payload={"state": "down", "nic": "mlx5_0"},
    )
    assert render_event_line(e) == "fabric.port_state nic=mlx5_0 state=down"


@pytest.mark.parametrize(
    ("overrides", "match"),
    [
        (
            {
                "events": [
                    {"ref": "e1", "ts_utc_ns": 20, "text": "a.b"},
                    {"ref": "e2", "ts_utc_ns": 10, "text": "a.b"},
                ]
            },
            "time-ordered",
        ),
        (
            {
                "events": [
                    {"ref": "e1", "ts_utc_ns": 10, "text": "a.b"},
                    {"ref": "e1", "ts_utc_ns": 20, "text": "a.b"},
                ]
            },
            "unique",
        ),
        ({"incident_id": "other"}, "different incident"),
        ({"events": [{"ref": "e2", "ts_utc_ns": 10, "text": "a.b"}]}, "evidence not in"),
    ],
)
def test_inconsistent_records_are_rejected(overrides: dict[str, object], match: str) -> None:
    with pytest.raises(ValidationError, match=match):
        IncidentRecord.model_validate(_record(**overrides))


def test_hostnames_and_gpu_uuids_must_be_scrubbed() -> None:
    leaky = _record()
    leaky["labels"] = {
        "fault_id": "F08",
        "fault_class": "nic_link_down",
        "culprit": {"node": "gpu-host-17.example.internal", "nic": "mlx5_0"},
    }
    with pytest.raises(ValidationError, match="pseudonym"):
        IncidentRecord.model_validate(leaky)
    leaky["labels"] = {
        "fault_id": "F12",
        "fault_class": "gpu_hw_fault",
        "culprit": {"node": "n0", "gpu_uuid": "GPU-1234"},
    }
    with pytest.raises(ValidationError, match="scrubbed"):
        IncidentRecord.model_validate(leaky)
