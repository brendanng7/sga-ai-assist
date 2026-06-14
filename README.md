# SGA AI Assist - Local WhisperX Transcription

Local speech-to-text and speaker diarization service powered by WhisperX.

## What It Does

- Transcribes audio/video files with WhisperX.
- Aligns words for improved timestamps.
- Optionally assigns speaker labels with WhisperX diarization.
- Exposes both a CLI and a local FastAPI upload endpoint.

## Requirements

- Python 3.10 or 3.11
- `ffmpeg` available on `PATH`
- A Hugging Face read token for diarization
- Accepted access terms for the pyannote diarization model used by WhisperX

WhisperX documents the current install path as `pip install whisperx`, and diarization requires an HF token plus model access acceptance. See the upstream project: https://github.com/m-bain/whisperX

## Setup

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and set:

```bash
HF_TOKEN=hf_your_token_here
```

CPU works, but it is slower:

```bash
WHISPERX_DEVICE=cpu
WHISPERX_COMPUTE_TYPE=int8
```

For NVIDIA CUDA:

```bash
WHISPERX_DEVICE=cuda
WHISPERX_COMPUTE_TYPE=float16
```

## CLI Usage

Transcribe and diarize:

```bash
python -m sga_ai_assist.cli ./meeting.wav --diarize --output outputs/meeting.json
```

Known two-speaker recording:

```bash
python -m sga_ai_assist.cli ./meeting.wav --diarize --min-speakers 2 --max-speakers 2
```

Transcription only:

```bash
python -m sga_ai_assist.cli ./meeting.wav --no-diarize
```

## API Usage

Start the local server:

```bash
uvicorn sga_ai_assist.api:app --host 127.0.0.1 --port 8000
```

Upload an audio file:

```bash
curl -F "file=@meeting.wav" \
  -F "diarize=true" \
  -F "min_speakers=2" \
  -F "max_speakers=2" \
  http://127.0.0.1:8000/transcribe
```

The response includes segment timestamps, text, speaker labels when available, and word-level timestamps where WhisperX alignment can produce them.

## Docker

CPU container:

```bash
docker build -t sga-ai-assist .
docker run --rm -p 8000:8000 --env-file .env sga-ai-assist
```

For NVIDIA GPU acceleration, install the NVIDIA container runtime on the host and pass GPU access:

```bash
docker run --rm --gpus all -p 8000:8000 --env-file .env \
  -e WHISPERX_DEVICE=cuda \
  -e WHISPERX_COMPUTE_TYPE=float16 \
  sga-ai-assist
```

## Local Model Storage

By default, WhisperX uses its normal model cache. To keep models inside this workspace:

```bash
WHISPERX_MODEL_DIR=./models
```

The first run downloads models and can take a while.
