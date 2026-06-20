from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class WhisperXSettings:
    model: str = "large-v2"
    device: str = "cpu"
    compute_type: str = "int8"
    batch_size: int = 8
    threads: int = 4
    language: str | None = None
    align_model: str | None = None
    hf_token: str | None = None
    model_dir: Path | None = None


def get_settings() -> WhisperXSettings:
    model_dir = os.getenv("WHISPERX_MODEL_DIR")
    return WhisperXSettings(
        model=os.getenv("WHISPERX_MODEL", "large-v2"),
        device=os.getenv("WHISPERX_DEVICE", "cpu"),
        compute_type=os.getenv("WHISPERX_COMPUTE_TYPE", "int8"),
        batch_size=int(os.getenv("WHISPERX_BATCH_SIZE", "8")),
        threads=int(os.getenv("WHISPERX_THREADS", "4")),
        language=os.getenv("WHISPERX_LANGUAGE") or None,
        align_model=os.getenv("WHISPERX_ALIGN_MODEL") or None,
        hf_token=os.getenv("HF_TOKEN") or None,
        model_dir=Path(model_dir).expanduser() if model_dir else None,
    )
