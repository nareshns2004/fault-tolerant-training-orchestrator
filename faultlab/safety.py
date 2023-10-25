"""Host allowlist enforcement (CLAUDE.md rule 5). Default-deny.

The allowlist lives in ``configs/hosts.local.yaml`` (gitignored — hostnames may be
sensitive; see CLAUDE.md rule 6). ``configs/hosts.example.yaml`` documents the format.
"""

from __future__ import annotations

import socket
from pathlib import Path

import yaml
from pydantic import Field

from goodput.schemas._base import SchemaModel


class HostNotAllowedError(PermissionError):
    pass


class HostAllowlist(SchemaModel):
    hosts: frozenset[str] = Field(default_factory=frozenset)

    def check(self, hostname: str) -> None:
        """Raise unless ``hostname`` is listed. Exact, case-insensitive; no wildcards."""
        if hostname.strip().lower() not in {h.lower() for h in self.hosts}:
            raise HostNotAllowedError(f"host {hostname!r} is not on the faultlab allowlist")

    def check_local(self) -> None:
        self.check(socket.gethostname())


def load_allowlist(path: Path) -> HostAllowlist:
    """Load the allowlist. A missing file yields an empty (deny-all) allowlist."""
    if not path.exists():
        return HostAllowlist()
    with path.open(encoding="utf-8") as fh:
        return HostAllowlist.model_validate(yaml.safe_load(fh) or {})
