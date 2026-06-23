# SGA AI Copilot

Small local transcription pipeline. This project intentionally does only one
thing: turn an audio/video file into a transcript JSON.

No diarization. No alignment. No SLM summarisation.

## Setup

From this folder:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
pip install -e .
cp .env.example .env
```

You also need `ffmpeg` on `PATH`.

## CPU Defaults

For CPU-only machines:

```bash
COPILOT_WHISPER_MODEL=small
COPILOT_DEVICE=cpu
COPILOT_COMPUTE_TYPE=int8
COPILOT_BATCH_SIZE=8
COPILOT_THREADS=4
COPILOT_LANGUAGE=en
```

For a 6-core / 12-thread CPU, try:

```bash
COPILOT_THREADS=6
```

## Usage

From the parent repository:

```bash
python -m sga_ai_copilot.cli meeting.wav --output sga_ai_copilot/outputs/meeting.json
```

Override language for one run:

```bash
python -m sga_ai_copilot.cli meeting.wav --language en --output sga_ai_copilot/outputs/meeting.json
```

Or from inside this folder after installing the console script:

```bash
sga-copilot-transcribe ../meeting.wav --output outputs/meeting.json
```

## Output Shape

```json
{
  "audio_file": "../meeting.wav",
  "settings": {
    "model": "small",
    "device": "cpu",
    "compute_type": "int8",
    "batch_size": 8,
    "threads": 4,
    "language": "en",
    "model_dir": null
  },
  "language": "en",
  "segments": [
    {
      "start": 0.0,
      "end": 5.0,
      "text": "..."
    }
  ]
}
```
