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
    slm_enabled: bool = False
    slm_provider: str = "ollama"
    slm_model: str = "llama3.1:8b"
    slm_base_url: str = "http://127.0.0.1:11434"
    slm_context_file: Path = Path("prompts/context.md")
    slm_temperature: float = 0.0
    slm_timeout_seconds: int = 180
    slm_max_input_chars: int = 16000


def get_settings() -> TranscriptionSettings:
    model_dir = os.getenv("COPILOT_MODEL_DIR")
    context_file = os.getenv("COPILOT_SLM_CONTEXT_FILE", "prompts/context.md")
    return TranscriptionSettings(
        model=os.getenv("COPILOT_WHISPER_MODEL", "small"),
        device=os.getenv("COPILOT_DEVICE", "cpu"),
        compute_type=os.getenv("COPILOT_COMPUTE_TYPE", "int8"),
        batch_size=int(os.getenv("COPILOT_BATCH_SIZE", "8")),
        threads=int(os.getenv("COPILOT_THREADS", "4")),
        language=os.getenv("COPILOT_LANGUAGE", "en") or None,
        model_dir=Path(model_dir).expanduser() if model_dir else None,
        slm_enabled=_env_bool("COPILOT_SLM_ENABLED", False),
        slm_provider=os.getenv("COPILOT_SLM_PROVIDER", "ollama"),
        slm_model=os.getenv("COPILOT_SLM_MODEL", "llama3.1:8b"),
        slm_base_url=os.getenv("COPILOT_SLM_BASE_URL", "http://127.0.0.1:11434"),
        slm_context_file=Path(context_file).expanduser(),
        slm_temperature=float(os.getenv("COPILOT_SLM_TEMPERATURE", "0")),
        slm_timeout_seconds=int(os.getenv("COPILOT_SLM_TIMEOUT_SECONDS", "180")),
        slm_max_input_chars=int(os.getenv("COPILOT_SLM_MAX_INPUT_CHARS", "16000")),
    )


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}
