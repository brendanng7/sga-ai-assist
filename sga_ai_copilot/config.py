from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


PROJECT_DIR = Path(__file__).resolve().parent
load_dotenv(PROJECT_DIR / ".env")


@dataclass(frozen=True)
class TranscriptionSettings:
    model: str = "small"
    device: str = "cpu"
    compute_type: str = "int8"
    batch_size: int = 8
    threads: int = 4
    language: str | None = "en"
    model_dir: Path | None = None


def get_settings() -> TranscriptionSettings:
    model_dir = os.getenv("COPILOT_MODEL_DIR")
    return TranscriptionSettings(
        model=os.getenv("COPILOT_WHISPER_MODEL", "small"),
        device=os.getenv("COPILOT_DEVICE", "cpu"),
        compute_type=os.getenv("COPILOT_COMPUTE_TYPE", "int8"),
        batch_size=int(os.getenv("COPILOT_BATCH_SIZE", "8")),
        threads=int(os.getenv("COPILOT_THREADS", "4")),
        language=os.getenv("COPILOT_LANGUAGE", "en") or None,
        model_dir=Path(model_dir).expanduser() if model_dir else None,
    )

