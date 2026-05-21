#!/bin/bash
set -e

git submodule update --remote --recursive

uv run python scripts/build_protos.py

uv build
uv pip install dist/gogi_python-0.1.0-py3-none-any.whl