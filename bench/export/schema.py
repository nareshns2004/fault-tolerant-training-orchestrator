"""Generate the published JSON Schema for ``IncidentRecord``.

``python -m bench.export.schema`` (or ``make schemas``) rewrites
``docs/schemas/incident.schema.json``. ``tests/unit/test_export_record.py`` fails if the
committed file differs from what the models generate, so the contract cannot drift silently.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from bench.export.record import RECORD_SCHEMA_V, IncidentRecord

SCHEMA_PATH = Path(__file__).resolve().parents[2] / "docs" / "schemas" / "incident.schema.json"
SCHEMA_ID = "https://github.com/nareshns2004/goodput-fault-tolerant-training-orchestrator/blob/main/docs/schemas/incident.schema.json"


def incident_record_json_schema() -> dict[str, Any]:
    schema = IncidentRecord.model_json_schema(mode="serialization")
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": SCHEMA_ID,
        "x-schema-version": RECORD_SCHEMA_V,
        **schema,
    }


def render() -> str:
    return json.dumps(incident_record_json_schema(), indent=2, sort_keys=True) + "\n"


def main() -> int:
    SCHEMA_PATH.parent.mkdir(parents=True, exist_ok=True)
    SCHEMA_PATH.write_text(render(), encoding="utf-8")
    sys.stdout.write(f"wrote {SCHEMA_PATH}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
