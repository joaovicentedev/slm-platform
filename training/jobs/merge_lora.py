from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from pathlib import Path

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer


ARTIFACT_DIR = Path(os.environ.get("MODEL_ARTIFACT_DIR", "/artifacts"))
BASE_MODEL_ID = os.environ.get("BASE_MODEL_ID", "HuggingFaceTB/SmolLM2-360M-Instruct")
LORA_ADAPTER_DIR = Path(os.environ.get("LORA_ADAPTER_DIR", ARTIFACT_DIR / "adapters" / "lora"))
MERGED_MODEL_DIR = Path(os.environ.get("MERGED_MODEL_DIR", ARTIFACT_DIR / "model"))


def resolve_dtype() -> torch.dtype | str:
    dtype = os.environ.get("MERGE_TORCH_DTYPE", "auto")
    if dtype == "auto":
        return "auto"
    if dtype == "float16":
        return torch.float16
    if dtype == "bfloat16":
        return torch.bfloat16
    if dtype == "float32":
        return torch.float32
    msg = "MERGE_TORCH_DTYPE must be one of auto, float16, bfloat16, or float32"
    raise ValueError(msg)


def main() -> None:
    if not LORA_ADAPTER_DIR.exists():
        msg = f"LoRA adapter directory does not exist: {LORA_ADAPTER_DIR}"
        raise FileNotFoundError(msg)

    MERGED_MODEL_DIR.mkdir(parents=True, exist_ok=True)

    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_ID)
    base_model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL_ID,
        torch_dtype=resolve_dtype(),
        device_map=os.environ.get("MERGE_DEVICE_MAP", "auto"),
    )
    adapter_model = PeftModel.from_pretrained(base_model, LORA_ADAPTER_DIR)
    merged_model = adapter_model.merge_and_unload()

    merged_model.save_pretrained(MERGED_MODEL_DIR, safe_serialization=True)
    tokenizer.save_pretrained(MERGED_MODEL_DIR)

    metadata = {
        "base_model_id": BASE_MODEL_ID,
        "lora_adapter_dir": str(LORA_ADAPTER_DIR),
        "merged_model_dir": str(MERGED_MODEL_DIR),
        "created_at": datetime.now(UTC).isoformat(),
        "serving_runtime": "vllm-openai",
    }
    with (MERGED_MODEL_DIR / "slm-artifact.json").open("w", encoding="utf-8") as file:
        json.dump(metadata, file, indent=2)

    print(f"Merged LoRA adapter into {MERGED_MODEL_DIR}")


if __name__ == "__main__":
    main()
