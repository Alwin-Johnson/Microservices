#!/usr/bin/env bash
set -e

cd "$(dirname "$0")/../environment"

cp ../solution/dependencies_fixed.py services/shared/db/dependencies.py
cp ../solution/base_fixed.py services/shared/clients/base.py

# Support rootless podman/docker setups
if [ -S "/run/user/$(id -u)/podman/podman.sock" ]; then
    export DOCKER_HOST="unix:///run/user/$(id -u)/podman/podman.sock"
fi

# Rebuild and restart the services to apply the code changes
docker compose build gateway orders payments inventory
docker compose up -d
