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
    llm_provider: str = "openrouter"
    llm_model: str = "nvidia/nemotron-3-ultra-550b-a55b:free"
    llm_base_url: str = "https://openrouter.ai/api/v1"
    llm_api_key: str | None = None
    llm_context_file: Path = Path("prompts/context.md")
    llm_temperature: float = 0.0
    llm_timeout_seconds: int = 180
    llm_max_input_chars: int = 16000
    llm_http_referer: str | None = None
    llm_app_title: str = "SGA AI Copilot"


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
        llm_provider=os.getenv("COPILOT_LLM_PROVIDER", "openrouter"),
        llm_model=os.getenv(
            "COPILOT_LLM_MODEL",
            "nvidia/nemotron-3-ultra-550b-a55b:free",
        ),
        llm_base_url=os.getenv(
            "COPILOT_LLM_BASE_URL",
            "https://openrouter.ai/api/v1",
        ),
        llm_api_key=os.getenv("COPILOT_LLM_API_KEY") or None,
        llm_temperature=float(os.getenv("COPILOT_LLM_TEMPERATURE", "0")),
        llm_timeout_seconds=int(os.getenv("COPILOT_LLM_TIMEOUT_SECONDS", "180")),
        llm_max_input_chars=int(os.getenv("COPILOT_LLM_MAX_INPUT_CHARS", "16000")),
        llm_http_referer=os.getenv("COPILOT_LLM_HTTP_REFERER") or None,
        llm_app_title=os.getenv("COPILOT_LLM_APP_TITLE", "SGA AI Copilot"),
    )
