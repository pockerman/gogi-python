#!/bin/bash


pip install uv
uv sync
python scripts/build_protos.py
uv build