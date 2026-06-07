from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from pathlib import Path


ARTIFACT_DIR = Path(os.environ.get("MODEL_ARTIFACT_DIR", "/artifacts"))
METADATA_PATH = ARTIFACT_DIR / "model-metadata.json"


def main() -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    metadata = {
        "model_name": "LFM2.5-350M",
        "artifact_version": "local-dev",
        "created_at": datetime.now(UTC).isoformat(),
        "runtime": "smoke-train",
        "notes": (
            "Placeholder artifact written by the local training container. "
            "Replace this module with the real fine-tuning pipeline."
        ),
    }

    with METADATA_PATH.open("w", encoding="utf-8") as file:
        json.dump(metadata, file, indent=2)

    print(f"Wrote artifact metadata to {METADATA_PATH}")


if __name__ == "__main__":
    main()
