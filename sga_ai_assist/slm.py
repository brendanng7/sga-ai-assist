from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .config import WhisperXSettings


CATEGORIES = ("Health", "Social", "Financial", "WMTY", "Others")


@dataclass(frozen=True)
class CategorizationOptions:
    enabled: bool
    model: str | None = None
    prompt_file: Path | None = None


class SlmCategorizer:
    def __init__(self, settings: WhisperXSettings) -> None:
        self.settings = settings

    def categorize(
        self,
        segments: list[dict[str, Any]],
        options: CategorizationOptions,
    ) -> dict[str, Any]:
        model = options.model or self.settings.slm_model
        prompt_file = options.prompt_file or self.settings.slm_prompt_file
        prompt = self._build_prompt(prompt_file, segments)

        if self.settings.slm_provider != "ollama":
            raise ValueError(
                f"Unsupported SLM provider: {self.settings.slm_provider!r}"
            )

        raw_response = self._call_ollama(model, prompt)
        parsed = _parse_json_object(raw_response)

        return {
            "enabled": True,
            "provider": self.settings.slm_provider,
            "model": model,
            "prompt_file": str(prompt_file),
            "segments": _normalise_categories(parsed),
            "raw_response": raw_response,
        }

    def _build_prompt(
        self,
        prompt_file: Path,
        segments: list[dict[str, Any]],
    ) -> str:
        if not prompt_file.exists():
            raise FileNotFoundError(f"SLM prompt file not found: {prompt_file}")

        template = prompt_file.read_text(encoding="utf-8")
        transcript = _segments_to_transcript(segments)
        if len(transcript) > self.settings.slm_max_input_chars:
            transcript = transcript[: self.settings.slm_max_input_chars]

        return template.replace("{{TRANSCRIPT}}", transcript)

    def _call_ollama(self, model: str, prompt: str) -> str:
        payload = json.dumps(
            {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "format": "json",
                "options": {
                    "temperature": self.settings.slm_temperature,
                },
            }
        ).encode("utf-8")
        url = self.settings.slm_base_url.rstrip("/") + "/api/generate"
        request = urllib.request.Request(
            url,
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
                "Could not reach local SLM server. Start Ollama or disable "
                "categorization with --no-categorize."
            ) from exc

        return str(body.get("response", "")).strip()


def disabled_categorization(settings: WhisperXSettings) -> dict[str, Any]:
    return {
        "enabled": False,
        "provider": settings.slm_provider,
        "model": settings.slm_model,
        "prompt_file": str(settings.slm_prompt_file),
        "segments": _empty_categories(),
    }


def _segments_to_transcript(segments: list[dict[str, Any]]) -> str:
    lines = []
    for segment in segments:
        start = segment.get("start")
        end = segment.get("end")
        speaker = segment.get("speaker", "UNKNOWN_SPEAKER")
        text = str(segment.get("text", "")).strip()
        timestamp = ""
        if isinstance(start, int | float) and isinstance(end, int | float):
            timestamp = f"[{start:.2f}-{end:.2f}] "
        lines.append(f"{timestamp}{speaker}: {text}")
    return "\n".join(lines)


def _parse_json_object(raw_response: str) -> dict[str, Any]:
    try:
        parsed = json.loads(raw_response)
    except json.JSONDecodeError as exc:
        raise ValueError("SLM response was not valid JSON.") from exc
    if not isinstance(parsed, dict):
        raise ValueError("SLM response must be a JSON object.")
    return parsed


def _normalise_categories(parsed: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    source = parsed.get("segments", parsed)
    if not isinstance(source, dict):
        source = parsed
    lower_key_map = {key.lower(): key for key in source}
    categories = _empty_categories()
    for category in CATEGORIES:
        source_key = category
        if source_key not in source:
            source_key = lower_key_map.get(category.lower(), category)
        value = source.get(source_key, [])
        if isinstance(value, str):
            value = [{"summary": value, "evidence": []}]
        if not isinstance(value, list):
            value = []
        categories[category] = [
            _normalise_item(item)
            for item in value
            if isinstance(item, dict | str)
        ]
    return categories


def _normalise_item(item: dict[str, Any] | str) -> dict[str, Any]:
    if isinstance(item, str):
        return {"summary": item, "evidence": []}

    summary = str(item.get("summary", "")).strip()
    evidence = item.get("evidence", [])
    if isinstance(evidence, str):
        evidence = [evidence]
    if not isinstance(evidence, list):
        evidence = []

    return {
        "summary": summary,
        "evidence": [str(entry).strip() for entry in evidence if str(entry).strip()],
    }


def _empty_categories() -> dict[str, list[dict[str, Any]]]:
    return {category: [] for category in CATEGORIES}
