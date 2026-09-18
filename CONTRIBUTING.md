# Contributing

Thanks for contributing to gogi-python. This document covers how to set up your environment, the
checks your pull request needs to pass, and the commit message format we enforce.

## Development setup

- Fetch the proto submodule:

  ```
  git submodule update --remote --recursive
  ```

- Create and activate a virtual environment for the SDK (do not install system-wide), e.g.:

  ```
  conda create -n gogi-python-3.12 python=3.12
  conda activate gogi-python-3.12
  ```

- Install [`uv`](https://github.com/astral-sh/uv) and sync dependencies:

  ```
  pip install uv
  uv sync --extra dev
  ```

- Generate the protobuf/gRPC code:

  ```
  uv run python scripts/build_protos.py
  ```

## Before opening a pull request

CI runs three checks on every pull request; run them locally first so review isn't blocked on
mechanical issues:

- **Lint** — `uv run ruff check .`
- **Format** — `uv run ruff format --check .` (fix locally with `uv run ruff format .`)
- **Tests** — `uv run pytest tests -v --cov=gogi --cov-report=term-missing`

## Commit messages

All commits on a pull request must follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>[optional scope][!]: <description>
```

- `type` is one of: `build`, `chore`, `ci`, `docs`, `feat`, `fix`, `perf`, `refactor`, `revert`,
  `style`, `test`.
- `scope` is optional and describes the affected area, e.g. `feat(workflow): ...`.
- Append `!` before the colon for a breaking change, e.g. `fix!: ...`.
- `description` is a short summary in the imperative mood (e.g. "add", not "added"/"adds").

Examples:

```
feat: add workflow client
fix(clients): handle missing provider in run_stream
docs: update installation instructions
```

Merge commits are exempt. A `Conventional Commits` GitHub Action checks every commit on a pull
request and fails the build if any commit message doesn't conform — fix commit messages (e.g. via
`git commit --amend` or an interactive rebase) before requesting review.

## Pull requests

- Keep pull requests focused on a single change; avoid bundling unrelated fixes or refactors.
- Make sure `git submodule update --remote --recursive` has been run so generated proto changes
  aren't accidentally omitted or stale.
- Add or update tests for any behavior change.
- Ensure lint, format, and test checks above pass before requesting review.
