# syntax=docker/dockerfile:1.6
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install minimal build tooling for wheels
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency metadata first for better caching
COPY pyproject.toml README.md ./
COPY src ./src

# Install project dependencies
RUN pip install --upgrade pip \
    && pip install .

# Copy any remaining application resources
COPY index.html ./index.html

EXPOSE 8000

CMD ["uvicorn", "ouchi_face.main:app", "--host", "0.0.0.0", "--port", "8000"]
