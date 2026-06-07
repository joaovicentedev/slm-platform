---
name: pytest
description: Run Python tests for this repository with pytest. Use when the user asks to run, debug, add, or verify pytest tests.
---

# Pytest

Use this repo's `uv` environment. The `dev` group is installed by default via:

```bash
uv sync
```

Run all pytest tests:

```bash
uv run pytest
```

Run a focused test file or test node:

```bash
uv run pytest path/to/test_file.py -q
uv run pytest path/to/test_file.py::test_name -q
```

If pytest dependencies are missing, run `uv sync` first. For the broader local verification suite, use:

```bash
make test
```
