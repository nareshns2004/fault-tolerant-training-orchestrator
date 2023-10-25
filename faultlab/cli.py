"""``faultlab`` command-line entry point."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from faultlab.scenario import load_scenario


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="faultlab", description="Fault injection harness")
    sub = parser.add_subparsers(dest="cmd", required=True)
    val = sub.add_parser("validate", help="validate a scenario YAML without injecting")
    val.add_argument("scenario", type=Path)
    args = parser.parse_args(argv)

    if args.cmd == "validate":
        scenario = load_scenario(args.scenario)
        sys.stdout.write(f"ok: {scenario.id} ({len(scenario.faults)} faults)\n")
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
