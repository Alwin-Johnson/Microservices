#!/usr/bin/env bash
set -e

cd "$(dirname "$0")/.."

echo "========================================"
echo " Resetting Platform Environment"
echo "========================================"

# Support rootless podman
if [ -S "/run/user/$(id -u)/podman/podman.sock" ]; then
    export DOCKER_HOST="unix:///run/user/$(id -u)/podman/podman.sock"
fi

echo "Running docker compose down..."
docker compose down --volumes --remove-orphans
docker compose rm -f

echo "Cleaning up local files..."
if [ -f .env ]; then
    echo "Removing .env file..."
    rm -f .env
fi

echo "Removing Python cache and temporary files..."
find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type d -name ".pytest_cache" -exec rm -r {} + 2>/dev/null || true

echo "========================================"
echo " Platform reset successfully."
echo "========================================"
