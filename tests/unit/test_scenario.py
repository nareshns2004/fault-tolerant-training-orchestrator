from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from faultlab.cli import main
from faultlab.scenario import Scenario, load_scenario

EXAMPLES = sorted((Path(__file__).resolve().parents[2] / "faultlab" / "scenarios").glob("*.yaml"))


@pytest.mark.parametrize("path", EXAMPLES, ids=lambda p: p.name)
def test_shipped_scenarios_validate(path: Path) -> None:
    assert load_scenario(path).faults


def _fault(**kw: object) -> dict[str, object]:
    base: dict[str, object] = {
        "fault_id": "F05",
        "target": {"rank": 0},
        "trigger": {"kind": "step", "step": 10},
        "revert_timeout_s": 60,
    }
    base.update(kw)
    return base


def _scenario(*faults: dict[str, object]) -> dict[str, object]:
    return {"id": "t", "seed": 1, "faults": list(faults)}


def test_revert_timeout_is_mandatory() -> None:
    f = _fault()
    del f["revert_timeout_s"]
    with pytest.raises(ValidationError, match="revert_timeout_s"):
        Scenario.model_validate(_scenario(f))


def test_duration_cannot_outlive_watchdog() -> None:
    with pytest.raises(ValidationError, match="watchdog"):
        Scenario.model_validate(_scenario(_fault(duration_s=120)))


def test_target_must_be_unambiguous() -> None:
    with pytest.raises(ValidationError, match="exactly one"):
        Scenario.model_validate(_scenario(_fault(target={"rank": 0, "node": "n"})))


def test_trigger_is_discriminated() -> None:
    s = Scenario.model_validate(_scenario(_fault(trigger={"kind": "poisson", "mtbf_s": 900})))
    assert s.faults[0].trigger.kind == "poisson"


def test_cli_validate(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["validate", str(EXAMPLES[0])]) == 0
    assert capsys.readouterr().out.startswith("ok:")
