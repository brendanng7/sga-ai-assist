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
    slm_enabled: bool = False
    slm_provider: str = "ollama"
    slm_model: str = "llama3.2:3b"
    slm_base_url: str = "http://127.0.0.1:11434"
    slm_prompt_file: Path = Path("prompts/slm_context.md")
    slm_temperature: float = 0.0
    slm_timeout_seconds: int = 180
    slm_max_input_chars: int = 16000


def get_settings() -> WhisperXSettings:
    model_dir = os.getenv("WHISPERX_MODEL_DIR")
    slm_prompt_file = os.getenv("SLM_PROMPT_FILE", "prompts/slm_context.md")
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
        slm_enabled=_env_bool("SLM_ENABLED", False),
        slm_provider=os.getenv("SLM_PROVIDER", "ollama"),
        slm_model=os.getenv("SLM_MODEL", "llama3.2:3b"),
        slm_base_url=os.getenv("SLM_BASE_URL", "http://127.0.0.1:11434"),
        slm_prompt_file=Path(slm_prompt_file).expanduser(),
        slm_temperature=float(os.getenv("SLM_TEMPERATURE", "0")),
        slm_timeout_seconds=int(os.getenv("SLM_TIMEOUT_SECONDS", "180")),
        slm_max_input_chars=int(os.getenv("SLM_MAX_INPUT_CHARS", "16000")),
    )


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}
