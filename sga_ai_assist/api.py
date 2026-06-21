from __future__ import annotations

import tempfile
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from starlette.concurrency import run_in_threadpool

from .config import get_settings
from .pipeline import TranscriptionOptions, WhisperXTranscriber


app = FastAPI(title="SGA AI Assist WhisperX API")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/transcribe")
async def transcribe(
    file: UploadFile = File(...),
    diarize: bool = Form(True),
    align: bool = Form(True),
    require_align: bool = Form(False),
    align_model: str | None = Form(None),
    min_speakers: int | None = Form(None),
    max_speakers: int | None = Form(None),
    language: str | None = Form(None),
    categorize: bool | None = Form(None),
    slm_model: str | None = Form(None),
    slm_prompt_file: str | None = Form(None),
) -> dict:
    suffix = Path(file.filename or "audio").suffix
    try:
        with tempfile.NamedTemporaryFile(delete=True, suffix=suffix) as audio_file:
            while chunk := await file.read(1024 * 1024):
                audio_file.write(chunk)
            audio_file.flush()

            return await run_in_threadpool(
                WhisperXTranscriber(get_settings()).transcribe,
                audio_file.name,
                TranscriptionOptions(
                    diarize=diarize,
                    align=align,
                    require_align=require_align,
                    align_model=align_model,
                    min_speakers=min_speakers,
                    max_speakers=max_speakers,
                    language=language,
                    categorize=categorize,
                    slm_model=slm_model,
                    slm_prompt_file=Path(slm_prompt_file) if slm_prompt_file else None,
                ),
            )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
