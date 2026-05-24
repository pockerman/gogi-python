# gogi-python

Python SDK for <a href="https://github.com/pockerman/gogi">gogi[AI]</a> platform.

## Installation



- Create a virtual environment for the SDK (do not install the SDK system-wide)
- Activate the virtual environment e.g.

```commandline
conda activate gogi-python-3.12
```

- Install ```uv``` package manager using pip

```commandline
pip install uv
```

Fetch the protos

```
git submodule update --remote --recursive
```

Build the protos

```commandline
uv run python scripts/build_protos.py
```

Build the package

```commandline
uv build
```

Install locally

```commandline
uv pip install dist/*.whl
```
