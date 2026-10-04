#!/usr/bin/env bash
#
# Installs the gogi-python SDK.
#
# This script assumes an appropriate virtual environment has already been
# created and activated (see README.md). It does not create or activate one.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

# Fetch the protos
git submodule update --remote --recursive

# Install uv package manager
pip install uv

# Build the protos
uv run python scripts/build_protos.py

# Build the package and install locally.
# `uv run` always executes inside the project's own .venv, which can differ
# from any separately activated virtual environment (e.g. a conda env), so
# install explicitly into .venv to make sure `uv run` can find the package.
uv build
uv pip install --python .venv/bin/python dist/*.whl

echo "gogi-python installed successfully"
