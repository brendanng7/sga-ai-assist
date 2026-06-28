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
        resolved_model = model or self.settings.llm_model
        resolved_context_file = context_file or self.settings.llm_context_file
        prompt = self._build_prompt(resolved_context_file, segments)

        if self.settings.llm_provider != "openrouter":
            raise ValueError(
                f"Unsupported LLM provider: {self.settings.llm_provider!r}"
            )

        response = self._call_openrouter(resolved_model, prompt)
        return {
            "enabled": True,
            "provider": self.settings.llm_provider,
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
            raise FileNotFoundError(f"LLM context file not found: {context_file}")

        context = context_file.read_text(encoding="utf-8")
        transcript = _segments_to_transcript(segments)
        if len(transcript) > self.settings.llm_max_input_chars:
            transcript = transcript[: self.settings.llm_max_input_chars]

        if "{{TRANSCRIPT}}" in context:
            return context.replace("{{TRANSCRIPT}}", transcript)
        return context.replace("[INSERT RAW TRANSCRIPT TEXT HERE]", transcript)

    def _call_openrouter(self, model: str, prompt: str) -> str:
        if not self.settings.llm_api_key:
            raise ValueError(
                "OpenRouter analysis requires COPILOT_LLM_API_KEY. "
                "Set it in sga_ai_copilot/.env or rerun without --analyze."
            )

        payload = json.dumps(
            {
                "model": model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                "temperature": self.settings.llm_temperature,
            }
        ).encode("utf-8")
        headers = {
            "Authorization": f"Bearer {self.settings.llm_api_key}",
            "Content-Type": "application/json",
        }
        if self.settings.llm_http_referer:
            headers["HTTP-Referer"] = self.settings.llm_http_referer
        if self.settings.llm_app_title:
            headers["X-OpenRouter-Title"] = self.settings.llm_app_title

        request = urllib.request.Request(
            self.settings.llm_base_url.rstrip("/") + "/chat/completions",
            data=payload,
            headers=headers,
            method="POST",
        )

        try:
            with urllib.request.urlopen(
                request,
                timeout=self.settings.llm_timeout_seconds,
            ) as response:
                body = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="replace")
            raise ConnectionError(
                "OpenRouter request failed "
                f"with HTTP {exc.code}: {error_body or exc.reason}"
            ) from exc
        except urllib.error.URLError as exc:
            raise ConnectionError(
                "Could not reach OpenRouter. Check network access and "
                "COPILOT_LLM_BASE_URL, or rerun without --analyze."
            ) from exc

        try:
            return str(body["choices"][0]["message"]["content"]).strip()
        except (KeyError, IndexError, TypeError) as exc:
            raise ValueError(f"Unexpected OpenRouter response shape: {body}") from exc


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
