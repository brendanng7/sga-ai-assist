# SGA AI Copilot

Small local transcription pipeline. This project intentionally does only one
thing first: turn an audio/video file into a transcript JSON. It can optionally
send that transcript to an LLM API for structured analysis.

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

## LLM API Defaults

The optional analysis stage uses OpenRouter by default. Create an OpenRouter API
key, then configure:

```bash
COPILOT_LLM_ENABLED=false
COPILOT_LLM_PROVIDER=openrouter
COPILOT_LLM_MODEL=nvidia/nemotron-3-ultra-550b-a55b:free
COPILOT_LLM_BASE_URL=https://openrouter.ai/api/v1
COPILOT_LLM_API_KEY=sk-or-v1-your-key
COPILOT_LLM_CONTEXT_FILE=prompts/context.md
COPILOT_LLM_TEMPERATURE=0
COPILOT_LLM_TIMEOUT_SECONDS=180
COPILOT_LLM_MAX_INPUT_CHARS=16000
COPILOT_LLM_HTTP_REFERER=
COPILOT_LLM_APP_TITLE=SGA AI Copilot
```

The default context prompt is the repository-level `prompts/context.md`.

## Usage

From the parent repository:

```bash
python -m sga_ai_copilot.cli meeting.wav --output sga_ai_copilot/outputs/meeting.json
```

Transcribe and analyze with the LLM API:

```bash
python -m sga_ai_copilot.cli meeting.wav \
  --analyze \
  --output sga_ai_copilot/outputs/meeting-analyzed.json
```

Override language for one run:

```bash
python -m sga_ai_copilot.cli meeting.wav --language en --output sga_ai_copilot/outputs/meeting.json
```

Override the LLM model or context prompt for one run:

```bash
python -m sga_ai_copilot.cli meeting.wav \
  --analyze \
  --llm-model nvidia/nemotron-3-ultra-550b-a55b:free \
  --llm-context-file prompts/context.md \
  --output sga_ai_copilot/outputs/meeting-analyzed.json
```

python -m sga_ai_copilot.cli sample.wav \
  --analyze \
  --llm-context-file prompts/context.md \
  --output sga_ai_copilot/outputs/sample-analyzed.json

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
    "provider": "openrouter",
    "model": "nvidia/nemotron-3-ultra-550b-a55b:free",
    "context_file": "prompts/context.md",
    "format": "markdown",
    "content": "..."
  }
}
```
