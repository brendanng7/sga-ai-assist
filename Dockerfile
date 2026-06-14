FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -U pip \
    && pip install --no-cache-dir -r requirements.txt

COPY sga_ai_assist ./sga_ai_assist
COPY pyproject.toml README.md ./

EXPOSE 8000

CMD ["uvicorn", "sga_ai_assist.api:app", "--host", "0.0.0.0", "--port", "8000"]

