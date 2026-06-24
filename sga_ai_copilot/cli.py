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
    parser.add_argument("--analyze", dest="analyze", action="store_true")
    parser.add_argument("--no-analyze", dest="analyze", action="store_false")
    parser.set_defaults(analyze=None)
    parser.add_argument("--slm-model")
    parser.add_argument("--slm-context-file", type=Path)
    args = parser.parse_args()

    result = SimpleTranscriber(get_settings()).transcribe(
        args.audio,
        language=args.language,
        analyze=args.analyze,
        slm_model=args.slm_model,
        slm_context_file=args.slm_context_file,
    )
    payload = json.dumps(result, indent=2, ensure_ascii=False)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload)


if __name__ == "__main__":
    main()
