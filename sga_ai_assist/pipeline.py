from __future__ import annotations

import gc
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .config import WhisperXSettings


@dataclass(frozen=True)
class TranscriptionOptions:
    diarize: bool = True
    align: bool = True
    require_align: bool = False
    align_model: str | None = None
    min_speakers: int | None = None
    max_speakers: int | None = None
    language: str | None = None


class WhisperXTranscriber:
    def __init__(self, settings: WhisperXSettings) -> None:
        self.settings = settings

    def transcribe(
        self,
        audio_path: str | Path,
        options: TranscriptionOptions | None = None,
    ) -> dict[str, Any]:
        options = options or TranscriptionOptions()
        audio_path = Path(audio_path)
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        whisperx = _import_whisperx()
        audio = whisperx.load_audio(str(audio_path))
        language = options.language or self.settings.language
        warnings: list[str] = []
        alignment = {
            "enabled": options.align,
            "status": "skipped" if not options.align else "pending",
            "model": options.align_model or self.settings.align_model,
            "error": None,
        }

        model_kwargs: dict[str, Any] = {
            "compute_type": self.settings.compute_type,
            "threads": self.settings.threads,
        }
        if self.settings.model_dir:
            model_kwargs["download_root"] = str(self.settings.model_dir)
        if language:
            model_kwargs["language"] = language

        model = whisperx.load_model(
            self.settings.model,
            self.settings.device,
            **model_kwargs,
        )
        result = model.transcribe(
            audio,
            batch_size=self.settings.batch_size,
            language=language,
        )
        del model
        _release_accelerator_memory()

        if options.align:
            result = self._align(whisperx, audio, result, alignment, warnings, options)

        diarize_segments = None
        if options.diarize:
            diarize_segments = self._diarize(whisperx, audio, options)
            result = whisperx.assign_word_speakers(diarize_segments, result)

        return {
            "audio_file": str(audio_path),
            "settings": _public_settings(self.settings),
            "options": asdict(options),
            "language": result.get("language"),
            "alignment": alignment,
            "warnings": warnings,
            "segments": result.get("segments", []),
            "diarization": _serialize_diarization(diarize_segments),
        }

    def _align(
        self,
        whisperx: Any,
        audio: Any,
        result: dict[str, Any],
        alignment: dict[str, Any],
        warnings: list[str],
        options: TranscriptionOptions,
    ) -> dict[str, Any]:
        align_model_name = options.align_model or self.settings.align_model
        try:
            align_model, metadata = whisperx.load_align_model(
                language_code=result["language"],
                device=self.settings.device,
                model_name=align_model_name,
                model_dir=(
                    str(self.settings.model_dir) if self.settings.model_dir else None
                ),
            )
        except ValueError as exc:
            no_default_model = "No default align-model" in str(exc)
            if align_model_name or options.require_align or not no_default_model:
                raise
            alignment["status"] = "skipped"
            alignment["error"] = str(exc)
            warnings.append(
                "WhisperX has no default alignment model for detected language "
                f"{result['language']!r}. Segment timestamps and diarization were kept, "
                "but word-level timestamps were skipped. Pass --align-model with a "
                "compatible wav2vec2 model to enable alignment."
            )
            return result

        aligned = whisperx.align(
            result["segments"],
            align_model,
            metadata,
            audio,
            self.settings.device,
            return_char_alignments=False,
        )
        alignment["status"] = "completed"
        alignment["model"] = align_model_name or metadata.get("language")
        del align_model
        _release_accelerator_memory()
        return aligned

    def _diarize(
        self,
        whisperx: Any,
        audio: Any,
        options: TranscriptionOptions,
    ) -> Any:
        if not self.settings.hf_token:
            raise ValueError(
                "Diarization requires HF_TOKEN. Set it in .env or disable diarization."
            )

        from whisperx.diarize import DiarizationPipeline

        diarize_model = DiarizationPipeline(
            token=self.settings.hf_token,
            device=self.settings.device,
            cache_dir=str(self.settings.model_dir) if self.settings.model_dir else None,
        )
        kwargs = {
            key: value
            for key, value in {
                "min_speakers": options.min_speakers,
                "max_speakers": options.max_speakers,
            }.items()
            if value is not None
        }
        return diarize_model(audio, **kwargs)


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


def _public_settings(settings: WhisperXSettings) -> dict[str, Any]:
    data = asdict(settings)
    data["hf_token"] = bool(settings.hf_token)
    data["model_dir"] = str(settings.model_dir) if settings.model_dir else None
    return data


def _serialize_diarization(diarize_segments: Any) -> list[dict[str, Any]] | None:
    if diarize_segments is None:
        return None

    if hasattr(diarize_segments, "itertracks"):
        rows = []
        for turn, _, speaker in diarize_segments.itertracks(yield_label=True):
            rows.append(
                {
                    "start": float(turn.start),
                    "end": float(turn.end),
                    "speaker": str(speaker),
                }
            )
        return rows

    if hasattr(diarize_segments, "to_dict"):
        rows = []
        for row in diarize_segments.to_dict(orient="records"):
            item = {
                "start": float(row["start"]),
                "end": float(row["end"]),
                "speaker": str(row["speaker"]),
            }
            if "label" in row:
                item["label"] = str(row["label"])
            rows.append(item)
        return rows

    return [{"raw": str(diarize_segments)}]
