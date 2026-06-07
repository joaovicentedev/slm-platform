# Quickstart

This document is the current working quickstart for local development.
It should be updated as the training and serving pipeline becomes more complete.

## Current Status

- Local serving uses vLLM's OpenAI-compatible API server.
- Local training is still a scaffold job, but the LoRA merge/export step is wired.
- The expected merged model artifact path is `/artifacts/model`.
- If `VLLM_MODEL` is not set, serving falls back to `HuggingFaceTB/SmolLM2-135M-Instruct`.

## Requirements

- Python 3.13
- `uv`
- Docker
- Docker Compose

## Local Python Setup

Create or refresh the project environment:

```bash
uv sync
```

This project installs the `serving` and `dev` groups by default.

Verify the core packages:

```bash
make test-imports
```

Run the local verification suite, including pytest tests:

```bash
make test
```

## VS Code

If VS Code shows errors like `Import "fastapi" could not be resolved`, select the project interpreter:

```text
.venv/bin/python
```

The issue usually means VS Code is using a different interpreter, or the environment has not been synced yet.

## Docker Workflow

Build and start the local stack:

```bash
docker compose up serving
```

Current services:

- `training`: runs a placeholder local training job
- `serving`: runs `vllm/vllm-openai-cpu:latest-arm64` by default on Apple Silicon

The containers share a Docker volume for model artifacts.

The default local model is intentionally small for a MacBook CPU:

```text
HuggingFaceTB/SmolLM2-135M-Instruct
```

Useful local serving knobs:

```bash
VLLM_MODEL=HuggingFaceTB/SmolLM2-135M-Instruct
SERVED_MODEL_NAME=slm
VLLM_DTYPE=float16
VLLM_MAX_MODEL_LEN=512
VLLM_KV_CACHE_MEMORY_BYTES=268435456
```

## Training To Serving Flow

Target workflow:

1. Fine-tune with Hugging Face + PEFT.
2. Save the LoRA adapter to `/artifacts/adapters/lora`.
3. Merge the adapter into the base model:

```bash
make merge-lora
```

4. Serve the merged model with vLLM:

```bash
VLLM_MODEL=/artifacts/model SERVED_MODEL_NAME=slm docker compose up serving
```

5. Product code calls vLLM through the OpenAI-compatible API.

Current default base model in Compose:

```text
HuggingFaceTB/SmolLM2-135M-Instruct
```

## API

List models:

```bash
curl http://localhost:8000/v1/models
```

Generate text:

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H 'content-type: application/json' \
  -d '{
    "model": "slm",
    "messages": [{"role": "user", "content": "Explain Kubernetes in simple terms"}],
    "max_tokens": 80,
    "temperature": 0.7
  }'
```

The Python product-side client is in `serving/app/main.py` and uses:

```text
VLLM_BASE_URL=http://localhost:8000/v1
VLLM_API_KEY=not-needed
VLLM_MODEL=slm
```

## Project Files

- [pyproject.toml](/Users/joaovicentedev/Projects/slm-api/pyproject.toml)
- [Dockerfile](/Users/joaovicentedev/Projects/slm-api/Dockerfile)
- [docker-compose.yml](/Users/joaovicentedev/Projects/slm-api/docker-compose.yml)
- [serving/app/main.py](/Users/joaovicentedev/Projects/slm-api/serving/app/main.py)
- [training/jobs/smoke_train.py](/Users/joaovicentedev/Projects/slm-api/training/jobs/smoke_train.py)
- [training/jobs/merge_lora.py](/Users/joaovicentedev/Projects/slm-api/training/jobs/merge_lora.py)

## Known Limitations

- The training job does not fine-tune a real model yet.
- vLLM runs on MacBook CPU for local development, so generation will be slower than GPU serving.
- No automated tests cover the end-to-end training-to-serving path yet.

## Next Expected Update

The next useful update to this file should document:

- the real fine-tuning command
- where the trained model is exported
- how serving loads the exported artifact
- local evaluation steps before AWS deployment
