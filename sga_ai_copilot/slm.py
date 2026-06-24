from __future__ import annotations

import json
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from .config import TranscriptionSettings


class CopilotAnalyzer:
    def __init__(self, settings: TranscriptionSettings) -> None:
        self.settings = settings

    def analyze(
        self,
        segments: list[dict[str, Any]],
        model: str | None = None,
        context_file: Path | None = None,
    ) -> dict[str, Any]:
        resolved_model = model or self.settings.slm_model
        resolved_context_file = context_file or self.settings.slm_context_file
        prompt = self._build_prompt(resolved_context_file, segments)

        if self.settings.slm_provider != "ollama":
            raise ValueError(
                f"Unsupported SLM provider: {self.settings.slm_provider!r}"
            )

        response = self._call_ollama(resolved_model, prompt)
        return {
            "enabled": True,
            "provider": self.settings.slm_provider,
            "model": resolved_model,
            "context_file": str(resolved_context_file),
            "format": "markdown",
            "content": response,
        }

    def _build_prompt(
        self,
        context_file: Path,
        segments: list[dict[str, Any]],
    ) -> str:
        if not context_file.exists():
            raise FileNotFoundError(f"SLM context file not found: {context_file}")

        context = context_file.read_text(encoding="utf-8")
        transcript = _segments_to_transcript(segments)
        if len(transcript) > self.settings.slm_max_input_chars:
            transcript = transcript[: self.settings.slm_max_input_chars]

        if "{{TRANSCRIPT}}" in context:
            return context.replace("{{TRANSCRIPT}}", transcript)
        return context.replace("[INSERT RAW TRANSCRIPT TEXT HERE]", transcript)

    def _call_ollama(self, model: str, prompt: str) -> str:
        payload = json.dumps(
            {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": self.settings.slm_temperature,
                },
            }
        ).encode("utf-8")
        request = urllib.request.Request(
            self.settings.slm_base_url.rstrip("/") + "/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(
                request,
                timeout=self.settings.slm_timeout_seconds,
            ) as response:
                body = json.loads(response.read().decode("utf-8"))
        except urllib.error.URLError as exc:
            raise ConnectionError(
                "Could not reach local SLM server. Start Ollama or rerun without "
                "--analyze."
            ) from exc

        return str(body.get("response", "")).strip()


def disabled_analysis(settings: TranscriptionSettings) -> dict[str, Any]:
    return {
        "enabled": False,
        "provider": settings.slm_provider,
        "model": settings.slm_model,
        "context_file": str(settings.slm_context_file),
        "format": "markdown",
        "content": None,
    }


def _segments_to_transcript(segments: list[dict[str, Any]]) -> str:
    lines = []
    for segment in segments:
        start = segment.get("start")
        end = segment.get("end")
        text = str(segment.get("text", "")).strip()
        timestamp = ""
        if isinstance(start, int | float) and isinstance(end, int | float):
            timestamp = f"[{start:.2f}-{end:.2f}] "
        if text:
            lines.append(f"{timestamp}{text}")
    return "\n".join(lines)

