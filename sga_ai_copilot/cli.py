from __future__ import annotations

import argparse
import json
from pathlib import Path

from .config import get_settings
from .transcriber import SimpleTranscriber


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Transcribe audio locally with a simple WhisperX ASR pipeline."
    )
    parser.add_argument("audio", type=Path)
    parser.add_argument("--output", "-o", type=Path)
    parser.add_argument("--language")
    parser.add_argument("--llm-model", "--slm-model", dest="llm_model")
    args = parser.parse_args()

    result = SimpleTranscriber(get_settings()).transcribe(
        args.audio,
        language=args.language,
        llm_model=args.llm_model,
    )
    payload = json.dumps(result, indent=2, ensure_ascii=False)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload)


if __name__ == "__main__":
    main()
