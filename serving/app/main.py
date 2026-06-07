from __future__ import annotations

import os

from openai import OpenAI


VLLM_BASE_URL = os.environ.get("VLLM_BASE_URL", "http://localhost:8000/v1")
VLLM_API_KEY = os.environ.get("VLLM_API_KEY", "not-needed")
VLLM_MODEL = os.environ.get("VLLM_MODEL", "slm")


def build_client() -> OpenAI:
    return OpenAI(base_url=VLLM_BASE_URL, api_key=VLLM_API_KEY)


def generate_text(
    prompt: str,
    *,
    model: str = VLLM_MODEL,
    max_tokens: int = 100,
    temperature: float = 0.7,
) -> str:
    response = build_client().chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=temperature,
    )
    content = response.choices[0].message.content
    return content or ""


def main() -> None:
    prompt = os.environ.get("PROMPT", "Explain Kubernetes in simple terms")
    print(generate_text(prompt))


if __name__ == "__main__":
    main()
