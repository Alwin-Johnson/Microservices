FROM python:3.12-slim

# ── System dependencies ────────────────────────────────────────────────────────
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
    && rm -rf /var/lib/apt/lists/*

# ── Working directory ──────────────────────────────────────────────────────────
WORKDIR /app

# ── Copy shared library into image ─────────────────────────────────────────────
COPY services/shared /app/shared

# ── Install shared library's runtime dependencies ──────────────────────────────
RUN grep -vE '^(-e|#|pytest|ruff|mypy|$)' \
        /app/shared/requirements.txt \
    | pip install --no-cache-dir -r /dev/stdin

# ── Install service dependencies ───────────────────────────────────────────────
COPY services/payments/requirements.txt /app/requirements.txt
RUN grep -v '^\-e' /app/requirements.txt \
    | pip install --no-cache-dir -r /dev/stdin

# ── Copy service source ────────────────────────────────────────────────────────
COPY services/payments /app/service

# ── Runtime ────────────────────────────────────────────────────────────────────
WORKDIR /app/service
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app

EXPOSE 8002

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8002"]
