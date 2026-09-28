"""``goodput`` command-line entry point. Subcommands are added as components land."""

from __future__ import annotations

import argparse
import sys

from goodput import __version__


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="goodput", description=__doc__)
    parser.add_argument("--version", action="version", version=f"goodput {__version__}")
    parser.parse_args(argv)
    parser.print_help(sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
