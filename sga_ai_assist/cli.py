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
    parser.add_argument("--align", dest="align", action="store_true", default=True)
    parser.add_argument("--no-align", dest="align", action="store_false")
    parser.add_argument("--require-align", action="store_true")
    parser.add_argument("--align-model")
    parser.add_argument("--diarize", dest="diarize", action="store_true", default=True)
    parser.add_argument("--no-diarize", dest="diarize", action="store_false")
    parser.add_argument("--min-speakers", type=int)
    parser.add_argument("--max-speakers", type=int)
    parser.add_argument("--categorize", dest="categorize", action="store_true")
    parser.add_argument("--no-categorize", dest="categorize", action="store_false")
    parser.set_defaults(categorize=None)
    parser.add_argument("--slm-model")
    parser.add_argument("--slm-prompt-file", type=Path)
    args = parser.parse_args()

    result = WhisperXTranscriber(get_settings()).transcribe(
        args.audio,
        TranscriptionOptions(
            diarize=args.diarize,
            align=args.align,
            require_align=args.require_align,
            align_model=args.align_model,
            min_speakers=args.min_speakers,
            max_speakers=args.max_speakers,
            language=args.language,
            categorize=args.categorize,
            slm_model=args.slm_model,
            slm_prompt_file=args.slm_prompt_file,
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
