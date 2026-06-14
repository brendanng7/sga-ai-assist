from __future__ import annotations

import argparse
import json
from pathlib import Path

from .config import get_settings
from .pipeline import TranscriptionOptions, WhisperXTranscriber


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Transcribe audio locally with WhisperX and optional diarization."
    )
    parser.add_argument("audio", type=Path)
    parser.add_argument("--output", "-o", type=Path)
    parser.add_argument("--language")
    parser.add_argument("--diarize", dest="diarize", action="store_true", default=True)
    parser.add_argument("--no-diarize", dest="diarize", action="store_false")
    parser.add_argument("--min-speakers", type=int)
    parser.add_argument("--max-speakers", type=int)
    args = parser.parse_args()

    result = WhisperXTranscriber(get_settings()).transcribe(
        args.audio,
        TranscriptionOptions(
            diarize=args.diarize,
            min_speakers=args.min_speakers,
            max_speakers=args.max_speakers,
            language=args.language,
        ),
    )
    payload = json.dumps(result, indent=2, ensure_ascii=False)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload)


if __name__ == "__main__":
    main()

