from __future__ import annotations

import gc
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .config import TranscriptionSettings
from .llm import CopilotAnalyzer


class SimpleTranscriber:
    def __init__(self, settings: TranscriptionSettings) -> None:
        self.settings = settings

    def transcribe(
        self,
        audio_path: str | Path,
        language: str | None = None,
        llm_model: str | None = None,
    ) -> dict[str, Any]:
        audio_path = Path(audio_path)
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        whisperx = _import_whisperx()
        audio = whisperx.load_audio(str(audio_path))
        resolved_language = language or self.settings.language

        model_kwargs: dict[str, Any] = {
            "compute_type": self.settings.compute_type,
            "threads": self.settings.threads,
        }
        if self.settings.model_dir:
            model_kwargs["download_root"] = str(self.settings.model_dir)
        if resolved_language:
            model_kwargs["language"] = resolved_language

        model = whisperx.load_model(
            self.settings.model,
            self.settings.device,
            **model_kwargs,
        )
        try:
            result = model.transcribe(
                audio,
                batch_size=self.settings.batch_size,
                language=resolved_language,
            )
        finally:
            del model
            _release_accelerator_memory()

        analysis = CopilotAnalyzer(self.settings).analyze(
            result.get("segments", []),
            model=llm_model,
        )

        return {
            "audio_file": str(audio_path),
            "settings": _public_settings(self.settings),
            "language": result.get("language"),
            "segments": result.get("segments", []),
            "analysis": analysis,
        }


def _import_whisperx() -> Any:
    try:
        import whisperx
    except ImportError as exc:
        raise RuntimeError(
            "WhisperX is not installed. Run `pip install -r requirements.txt`."
        ) from exc
    return whisperx


def _release_accelerator_memory() -> None:
    gc.collect()
    try:
        import torch

        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    except ImportError:
        pass


def _public_settings(settings: TranscriptionSettings) -> dict[str, Any]:
    data = asdict(settings)
    data["model_dir"] = str(settings.model_dir) if settings.model_dir else None
    data["llm_api_key"] = bool(settings.llm_api_key)
    data["llm_context_file"] = str(settings.llm_context_file)
    return data
