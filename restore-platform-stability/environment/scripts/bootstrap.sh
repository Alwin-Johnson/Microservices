#!/usr/bin/env bash
set -e

cd "$(dirname "$0")/.."

echo "========================================"
echo " Bootstrapping Platform Environment"
echo "========================================"

if [ ! -f .env ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
fi

# Support rootless podman
if [ -S "/run/user/$(id -u)/podman/podman.sock" ]; then
    export DOCKER_HOST="unix:///run/user/$(id -u)/podman/podman.sock"
fi

echo "Building service images..."
docker compose build

echo "Starting platform..."
docker compose up -d

echo "Waiting for dependencies..."
./scripts/wait-for-db.sh

echo "Waiting for services to become healthy..."
# Sleep to give FastAPI apps time to bind
sleep 5
./scripts/healthcheck.sh

echo "========================================"
echo " Platform bootstrapped successfully!"
echo "========================================"
