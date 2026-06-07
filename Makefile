SHELL := /bin/zsh

COMPOSE := docker compose
UV := uv
PYTHON := ./.venv/bin/python

.PHONY: help sync lock test test-python test-compose test-imports test-training-imports test-serving test-client merge-lora docker-build docker-up docker-up-serving docker-up-training docker-down docker-logs docker-logs-serving docker-logs-training docker-ps docker-shell-serving docker-restart docker-config serve clean

help:
	@printf "Available targets:\n"
	@printf "  sync           Sync the local uv environment\n"
	@printf "  lock           Refresh uv.lock\n"
	@printf "  test           Run the current local verification suite\n"
	@printf "  test-python    Compile Python sources\n"
	@printf "  test-compose   Validate docker compose config\n"
	@printf "  test-imports   Verify core Python imports in .venv\n"
	@printf "  test-training-imports Verify training imports with the training group\n"
	@printf "  test-serving   Check a running vLLM OpenAI-compatible server\n"
	@printf "  test-client    Verify the product-side vLLM client imports\n"
	@printf "  merge-lora     Merge a LoRA adapter into /artifacts/model\n"
	@printf "  docker-build   Build Docker services\n"
	@printf "  docker-up      Start Docker services in detached mode\n"
	@printf "  docker-up-serving Start only the serving service in detached mode\n"
	@printf "  docker-up-training Start only the training service\n"
	@printf "  docker-down    Stop Docker services\n"
	@printf "  docker-logs    Tail Docker service logs\n"
	@printf "  docker-logs-serving Tail serving logs only\n"
	@printf "  docker-logs-training Tail training logs only\n"
	@printf "  docker-ps      Show Docker service status\n"
	@printf "  docker-shell-serving Open a shell in the serving container\n"
	@printf "  docker-restart Rebuild and restart Docker services\n"
	@printf "  docker-config  Render validated docker compose config\n"
	@printf "  serve          Run the vLLM OpenAI-compatible server with Docker\n"
	@printf "  clean          Remove local Python cache directories\n"

sync:
	$(UV) sync

lock:
	$(UV) lock

test: test-python test-compose test-imports

test-python:
	python3 -m compileall serving training

test-compose:
	$(COMPOSE) config

test-imports:
	$(PYTHON) -c "import openai; print(f'openai={openai.__version__}')"

test-training-imports:
	$(UV) run --group training python -c "import peft, transformers, torch; print(f'peft={peft.__version__} transformers={transformers.__version__} torch={torch.__version__}')"

test-serving:
	curl --retry 20 --retry-all-errors --retry-delay 2 -fsS http://localhost:8000/health

test-client:
	$(PYTHON) -c "from serving.app.main import build_client, generate_text; print(build_client().base_url); print(generate_text.__name__)"

merge-lora:
	$(UV) run --group training python -m training.jobs.merge_lora

docker-build:
	$(COMPOSE) build training

docker-up:
	$(COMPOSE) up --build -d

docker-up-serving:
	$(COMPOSE) up --build -d serving

docker-up-training:
	$(COMPOSE) up --build training

docker-down:
	$(COMPOSE) down

docker-logs:
	$(COMPOSE) logs -f

docker-logs-serving:
	$(COMPOSE) logs -f serving

docker-logs-training:
	$(COMPOSE) logs -f training

docker-ps:
	$(COMPOSE) ps

docker-shell-serving:
	$(COMPOSE) exec serving /bin/sh

docker-restart:
	$(COMPOSE) down
	$(COMPOSE) up --build -d

docker-config:
	$(COMPOSE) config

serve:
	$(COMPOSE) up serving

clean:
	find . -type d \( -name __pycache__ -o -name .pytest_cache -o -name .mypy_cache -o -name .ruff_cache \) -prune -exec rm -rf {} +
