# SGA AI Copilot

Small local transcription pipeline. This project intentionally does only one
thing first: turn an audio/video file into a transcript JSON. It can optionally
send that transcript to a local SLM for structured analysis.

No diarization. No alignment.

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

## Local SLM Defaults

The optional analysis stage expects an Ollama-compatible local server:

```bash
ollama pull llama3.1:8b
ollama serve
```

Then configure:

```bash
COPILOT_SLM_ENABLED=false
COPILOT_SLM_PROVIDER=ollama
COPILOT_SLM_MODEL=llama3.1:8b
COPILOT_SLM_BASE_URL=http://127.0.0.1:11434
COPILOT_SLM_CONTEXT_FILE=prompts/context.md
COPILOT_SLM_TEMPERATURE=0
COPILOT_SLM_TIMEOUT_SECONDS=180
COPILOT_SLM_MAX_INPUT_CHARS=16000
```

The default context prompt is the repository-level `prompts/context.md`.

## Usage

From the parent repository:

```bash
python -m sga_ai_copilot.cli meeting.wav --output sga_ai_copilot/outputs/meeting.json
```

Transcribe and analyze with the local SLM:

```bash
python -m sga_ai_copilot.cli meeting.wav \
  --analyze \
  --output sga_ai_copilot/outputs/meeting-analyzed.json
```

Override language for one run:

```bash
python -m sga_ai_copilot.cli meeting.wav --language en --output sga_ai_copilot/outputs/meeting.json
```

Override the SLM model or context prompt for one run:

```bash
python -m sga_ai_copilot.cli meeting.wav \
  --analyze \
  --slm-model llama3.1:8b \
  --slm-context-file prompts/context.md \
  --output sga_ai_copilot/outputs/meeting-analyzed.json
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
  ],
  "analysis": {
    "enabled": true,
    "provider": "ollama",
    "model": "llama3.1:8b",
    "context_file": "prompts/context.md",
    "format": "markdown",
    "content": "..."
  }
}
```
