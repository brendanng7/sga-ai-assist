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
WHISPERX_LANGUAGE=en
```

`WHISPERX_LANGUAGE=en` is recommended for Singaporean English recordings because
Whisper can otherwise mis-detect the first 30 seconds as Malay (`ms`).

CPU works, but it is slower:

```bash
WHISPERX_DEVICE=cpu
WHISPERX_COMPUTE_TYPE=int8
WHISPERX_THREADS=4
```

For a 6-core / 12-thread CPU such as a Ryzen 5 3600, try:

```bash
WHISPERX_THREADS=6
```

If the machine becomes sluggish during transcription, reduce it to `4`. If it
still has CPU headroom, try `8`.

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

If Whisper detects Singaporean English as Malay, force English explicitly:

```bash
python -m sga_ai_assist.cli ./meeting.wav --language en --diarize --min-speakers 2 --max-speakers 2
```

If WhisperX detects a language without a built-in alignment model, such as Malay
(`ms`), the app now keeps the transcript and diarization result and skips
word-level alignment by default. To make that explicit:

```bash
python -m sga_ai_assist.cli ./meeting.wav --diarize --no-align --min-speakers 2 --max-speakers 2
```

If you have tested a compatible Hugging Face wav2vec2 alignment model for that
language, pass it directly:

```bash
python -m sga_ai_assist.cli ./meeting.wav --diarize --align-model owner/model-name
```

You can also set it in `.env`:

```bash
WHISPERX_ALIGN_MODEL=owner/model-name
```

If the recording is actually Indonesian rather than Malay, try forcing
Indonesian because WhisperX includes a default Indonesian alignment model:

```bash
python -m sga_ai_assist.cli ./meeting.wav --language id --diarize --min-speakers 2 --max-speakers 2
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
  -F "align=true" \
  -F "min_speakers=2" \
  -F "max_speakers=2" \
  http://127.0.0.1:8000/transcribe
```

The response includes segment timestamps, text, speaker labels when available, and word-level timestamps where WhisperX alignment can produce them.

The `alignment` response field reports whether word alignment completed or was
skipped. Segment-level transcription and diarization can still succeed when
alignment is skipped.

## FFmpeg 8 And TorchCodec

On Ubuntu machines with FFmpeg 8, `pyannote.audio` may warn that `torchcodec`
cannot load FFmpeg shared libraries. This project passes preloaded waveform data
into diarization, so that warning is usually not the failure you need to chase
first. The run shown above failed because Malay alignment is unsupported by
default, not because of FFmpeg.

If you later need pyannote's built-in decoder directly, install a TorchCodec
version compatible with your PyTorch version and FFmpeg shared libraries.

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

## CPU Speed Tuning

On machines without an NVIDIA GPU, keep WhisperX on CPU:

```bash
WHISPERX_DEVICE=cpu
WHISPERX_COMPUTE_TYPE=int8
```

The `WHISPERX_THREADS` setting controls faster-whisper's CPU worker threads
during transcription. Start near the number of physical CPU cores, then adjust
based on responsiveness and throughput.
