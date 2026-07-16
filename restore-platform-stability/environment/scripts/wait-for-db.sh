#!/usr/bin/env bash
set -e

cd "$(dirname "$0")/.."

echo "Waiting for PostgreSQL to be ready..."

# Support rootless podman
if [ -S "/run/user/$(id -u)/podman/podman.sock" ]; then
    export DOCKER_HOST="unix:///run/user/$(id -u)/podman/podman.sock"
fi

MAX_RETRIES=30
COUNTER=0

# Use pg_isready inside the container to check if postgres is accepting connections
while ! docker compose exec -T postgres pg_isready -U ecommerce_user -d ecommerce > /dev/null 2>&1; do
    COUNTER=$((COUNTER + 1))
    if [ $COUNTER -ge $MAX_RETRIES ]; then
        echo "Timeout waiting for PostgreSQL."
        exit 1
    fi
    echo "Waiting for PostgreSQL..."
    sleep 2
done

echo "PostgreSQL is ready!"

echo "Waiting for Redis to be ready..."
COUNTER=0
while ! docker compose exec -T redis redis-cli ping > /dev/null 2>&1; do
    COUNTER=$((COUNTER + 1))
    if [ $COUNTER -ge $MAX_RETRIES ]; then
        echo "Timeout waiting for Redis."
        exit 1
    fi
    echo "Waiting for Redis..."
    sleep 2
done

echo "Redis is ready!"
