from __future__ import annotations

from types import SimpleNamespace

import pytest

from serving.app import main as app_main


def test_build_client_uses_configured_vllm_connection(monkeypatch: pytest.MonkeyPatch) -> None:
    captured_kwargs: dict[str, str] = {}

    class FakeOpenAI:
        def __init__(self, **kwargs: str) -> None:
            captured_kwargs.update(kwargs)

    monkeypatch.setattr(app_main, "OpenAI", FakeOpenAI)
    monkeypatch.setattr(app_main, "VLLM_BASE_URL", "http://vllm.example/v1")
    monkeypatch.setattr(app_main, "VLLM_API_KEY", "secret")

    client = app_main.build_client()

    assert isinstance(client, FakeOpenAI)
    assert captured_kwargs == {
        "base_url": "http://vllm.example/v1",
        "api_key": "secret",
    }


def test_generate_text_sends_chat_completion_request(monkeypatch: pytest.MonkeyPatch) -> None:
    captured_kwargs: dict[str, object] = {}

    class FakeCompletions:
        def create(self, **kwargs: object) -> SimpleNamespace:
            captured_kwargs.update(kwargs)
            return SimpleNamespace(
                choices=[
                    SimpleNamespace(
                        message=SimpleNamespace(content="Generated answer"),
                    ),
                ],
            )

    fake_client = SimpleNamespace(
        chat=SimpleNamespace(completions=FakeCompletions()),
    )
    monkeypatch.setattr(app_main, "build_client", lambda: fake_client)

    result = app_main.generate_text(
        "Explain Kubernetes",
        model="test-model",
        max_tokens=42,
        temperature=0.2,
    )

    assert result == "Generated answer"
    assert captured_kwargs == {
        "model": "test-model",
        "messages": [{"role": "user", "content": "Explain Kubernetes"}],
        "max_tokens": 42,
        "temperature": 0.2,
    }


def test_generate_text_returns_empty_string_when_response_content_is_empty(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeCompletions:
        def create(self, **kwargs: object) -> SimpleNamespace:
            return SimpleNamespace(
                choices=[
                    SimpleNamespace(
                        message=SimpleNamespace(content=None),
                    ),
                ],
            )

    fake_client = SimpleNamespace(
        chat=SimpleNamespace(completions=FakeCompletions()),
    )
    monkeypatch.setattr(app_main, "build_client", lambda: fake_client)

    assert app_main.generate_text("Say nothing") == ""


def test_main_uses_prompt_environment_variable(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    captured_prompts: list[str] = []

    def fake_generate_text(prompt: str) -> str:
        captured_prompts.append(prompt)
        return "Generated from env"

    monkeypatch.setenv("PROMPT", "Use this prompt")
    monkeypatch.setattr(app_main, "generate_text", fake_generate_text)

    app_main.main()

    assert captured_prompts == ["Use this prompt"]
    assert capsys.readouterr().out == "Generated from env\n"


def test_main_uses_default_prompt_when_environment_variable_is_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured_prompts: list[str] = []

    monkeypatch.delenv("PROMPT", raising=False)
    monkeypatch.setattr(app_main, "generate_text", captured_prompts.append)

    app_main.main()

    assert captured_prompts == ["Explain Kubernetes in simple terms"]
