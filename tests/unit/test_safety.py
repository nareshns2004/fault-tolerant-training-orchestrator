from __future__ import annotations

from pathlib import Path

import pytest

from faultlab.safety import HostAllowlist, HostNotAllowedError, load_allowlist


def test_missing_file_denies_everything(tmp_path: Path) -> None:
    with pytest.raises(HostNotAllowedError):
        load_allowlist(tmp_path / "absent.yaml").check("anything")


def test_exact_case_insensitive_match_only() -> None:
    allow = HostAllowlist(hosts=frozenset({"Node-A.example"}))
    allow.check("node-a.example")
    for bad in ("node-a", "node-a.example.evil", "node-b.example"):
        with pytest.raises(HostNotAllowedError):
            allow.check(bad)


def test_example_config_parses(repo_root: Path) -> None:
    allow = load_allowlist(repo_root / "configs" / "hosts.example.yaml")
    assert allow.hosts
