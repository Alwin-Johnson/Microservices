#!/usr/bin/env bash
# Lightweight state reset only. Do not abort if Docker is unavailable.
if command -v docker &> /dev/null && docker info &> /dev/null; then
    docker compose down --volumes --remove-orphans || true
    docker compose rm -f || true
fi
exit 0
