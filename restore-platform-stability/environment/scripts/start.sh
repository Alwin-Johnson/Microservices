#!/usr/bin/env bash
# If Docker is available, start the stack. Otherwise, just wait for it.
if command -v docker &> /dev/null && docker info &> /dev/null; then
    docker compose up -d || true
fi
./scripts/wait-for-db.sh || true
exit 0
