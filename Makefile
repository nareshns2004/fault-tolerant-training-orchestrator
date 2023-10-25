# goodput — developer entry points. Keep in sync with the "Commands" list in CLAUDE.md.
# Targets marked (stub) exist so the interface is fixed early; they fail loudly until built.

SHELL      := /bin/bash
PY         ?= python3.11
VENV       ?= .venv
BIN        := $(VENV)/bin
PKGS       := goodput faultlab bench

.DEFAULT_GOAL := help
.PHONY: help setup lint fmt typecheck test test-gpu test-multinode check \
        env-manifest topo bench report clean

help:  ## List targets
	@grep -hE '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | \
	  awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

setup:  ## Create .venv with CPU-only dev deps and install pre-commit hooks
	uv venv --python 3.11 $(VENV)
	uv pip install --python $(BIN)/python -e '.[dev]'
	$(BIN)/pre-commit install

lint:  ## ruff lint + format check
	$(BIN)/ruff check .
	$(BIN)/ruff format --check .

fmt:  ## Auto-format
	$(BIN)/ruff format .
	$(BIN)/ruff check --fix .

typecheck:  ## mypy --strict on all Python packages
	$(BIN)/mypy

test:  ## CPU-only unit + integration tests (no GPU, no network fabric)
	$(BIN)/pytest

test-gpu:  ## Single-node GPU tests (requires allowlisted host, see docs/ENVIRONMENT.md)
	$(BIN)/pytest -m gpu

test-multinode:  ## Multi-node tests (requires allowlisted hosts)
	$(BIN)/pytest -m multinode

check: lint typecheck test  ## Everything CI runs

env-manifest:  ## (stub, M1) Write env manifest + docs/ENVIRONMENT.md generated section
	@echo "env-manifest: not implemented yet (M1)" >&2; exit 2

topo:  ## (stub, M1) Topology discovery -> artifacts/topology.json
	@echo "topo: not implemented yet (M1)" >&2; exit 2

bench:  ## (stub, M1) Run an experiment: make bench SCENARIO=bench/scenarios/<x>.yaml
	@test -n "$(SCENARIO)" || { echo "usage: make bench SCENARIO=<path.yaml>" >&2; exit 2; }
	@echo "bench: not implemented yet (M1)" >&2; exit 2

report:  ## (stub, M1) Regenerate plots/tables: make report RUN=<run_id>
	@test -n "$(RUN)" || { echo "usage: make report RUN=<run_id>" >&2; exit 2; }
	@echo "report: not implemented yet (M1)" >&2; exit 2

clean:  ## Remove caches and build outputs (never touches bench/results)
	rm -rf .mypy_cache .pytest_cache .ruff_cache build dist *.egg-info .coverage htmlcov
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
