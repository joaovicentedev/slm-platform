# AGENTS.md

- Use `QUICKSTART.md` as the source of truth for local setup and workflow.
- Python version: 3.13. Manage dependencies with `uv`; run `uv sync` after dependency changes.
- Default local verification: `make test`. For pytest-specific checks, use the local Codex pytest skill.
- Serving uses vLLM's OpenAI-compatible API. Default model fallback: `HuggingFaceTB/SmolLM2-135M-Instruct`.
- Keep changes small and update `QUICKSTART.md` when setup, serving, training, or verification steps change.
- Generate tests for each class or function that you create. 
- When finish the work, run all the tests for ensure the modifications.
