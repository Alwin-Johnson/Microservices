FROM python:3.12-slim

# ── System dependencies ────────────────────────────────────────────────────────
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
    && rm -rf /var/lib/apt/lists/*

# ── Working directory ──────────────────────────────────────────────────────────
WORKDIR /app

# ── Copy shared library into image ─────────────────────────────────────────────
# Shared is mounted on PYTHONPATH rather than installed as a wheel.
# This avoids packaging complexity and is idiomatic for monorepo libraries.
COPY services/shared /app/shared

# ── Install shared library's runtime dependencies ──────────────────────────────
RUN grep -vE '^(-e|#|pytest|ruff|mypy|$)' \
        /app/shared/requirements.txt \
    | pip install --no-cache-dir -r /dev/stdin

# ── Install service dependencies ───────────────────────────────────────────────
# Strip the editable shared reference — shared is on PYTHONPATH instead.
COPY services/gateway/requirements.txt /app/requirements.txt
RUN grep -v '^\-e' /app/requirements.txt \
    | pip install --no-cache-dir -r /dev/stdin

# ── Copy service source ────────────────────────────────────────────────────────
COPY services/gateway /app/service

# ── Runtime ────────────────────────────────────────────────────────────────────
WORKDIR /app/service
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
