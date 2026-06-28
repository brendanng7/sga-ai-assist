# SGA AI Assist

Local audio transcription and analysis experiments for Singapore senior-support
workflows.

The current recommended project is **SGA AI Copilot**:

- simple WhisperX transcription
- no diarization
- no word alignment
- automatic LLM API analysis using `prompts/context.md`

The older `sga_ai_assist` package is still in this repository for reference, but
it includes diarization/alignment paths that are slower and more complex.

## Repository Layout

```text
sga_ai_copilot/       Current simple transcription + LLM analysis pipeline
sga_ai_assist/        Earlier WhisperX diarization/alignment pipeline
prompts/context.md    Default prompt for LLM analysis
outputs/              Local generated outputs, ignored by Git
models/               Optional local model cache, ignored by Git
```

## Requirements

- Python 3.10 or 3.11
- `ffmpeg` on `PATH`
- OpenRouter API key
- WhisperX dependencies from `requirements.txt`

The pipeline accepts audio formats that `ffmpeg` can decode, including `.m4a`
and `.wav`.

On Ubuntu:

```bash
sudo apt install ffmpeg
```

## Setup

From the repository root:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```

Create the Copilot environment file:

```bash
cp sga_ai_copilot/.env.example sga_ai_copilot/.env
```

Edit `sga_ai_copilot/.env`.

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

For LLM analysis through OpenRouter:

```bash
COPILOT_LLM_PROVIDER=openrouter
COPILOT_LLM_MODEL=nvidia/nemotron-3-ultra-550b-a55b:free
COPILOT_LLM_BASE_URL=https://openrouter.ai/api/v1
COPILOT_LLM_API_KEY=sk-or-v1-your-key
COPILOT_LLM_TEMPERATURE=0
COPILOT_LLM_TIMEOUT_SECONDS=180
COPILOT_LLM_MAX_INPUT_CHARS=16000
COPILOT_LLM_HTTP_REFERER=
COPILOT_LLM_APP_TITLE=SGA AI Copilot
```

`COPILOT_LLM_HTTP_REFERER` can be blank. Keep `sga_ai_copilot/.env` private; it
is ignored by Git.

## Get An OpenRouter API Key

1. Go to https://openrouter.ai.
2. Sign in or create an account.
3. Open **Keys** from your OpenRouter account dashboard.
4. Create a new API key.
5. Copy the key into `sga_ai_copilot/.env` as `COPILOT_LLM_API_KEY`.

OpenRouter API keys usually start with `sk-or-`. Do not commit this key.

## Run Locally

Every run transcribes the audio and then sends the transcript to the configured
LLM API for analysis.

```bash
python -m sga_ai_copilot.cli sample.m4a \
  --output outputs/sample-analyzed.json
```

Use a different OpenRouter model for one run:

```bash
python -m sga_ai_copilot.cli sample.m4a \
  --llm-model openrouter/free \
  --output outputs/sample-analyzed.json
```

Force English transcription:

```bash
python -m sga_ai_copilot.cli sample.m4a \
  --language en \
  --output outputs/sample-analyzed.json
```

## Output Shape

```json
{
  "audio_file": "sample.m4a",
  "settings": {
    "model": "small",
    "device": "cpu",
    "compute_type": "int8",
    "batch_size": 8,
    "threads": 4,
    "language": "en",
    "model_dir": null,
    "llm_provider": "openrouter",
    "llm_model": "nvidia/nemotron-3-ultra-550b-a55b:free",
    "llm_base_url": "https://openrouter.ai/api/v1",
    "llm_api_key": true,
    "llm_context_file": "prompts/context.md"
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

## Notes

- `outputs/`, `.env`, `models/`, and local audio files are ignored by Git.
- On AMD GPU machines, use CPU mode. The faster WhisperX GPU path is CUDA-first.
- The first transcription run may download WhisperX model files.
- Free OpenRouter models may be rate-limited or change availability. If the
  configured model is unavailable, try another free model slug with
  `--llm-model`.
