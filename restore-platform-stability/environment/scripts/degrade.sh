#!/usr/bin/env bash
# Manual local helper to toggle FAULT_MODE on a running service via
# `docker compose exec`. This is a convenience for local reproduction
# only -- the seeded incident itself is fully deterministic given a
# workload replay and FAULT_MODE=on set in docker-compose.yml/.env; the
# verifier never calls this script.
#
# Usage: ./scripts/degrade.sh on|off [service...]
set -euo pipefail

ACTION="${1:-on}"
shift || true
SERVICES=("$@")
if [[ ${#SERVICES[@]} -eq 0 ]]; then
  SERVICES=(gateway orders payments inventory)
fi

if [[ "$ACTION" != "on" && "$ACTION" != "off" ]]; then
  echo "usage: degrade.sh on|off [service...]" >&2
  exit 1
fi

for svc in "${SERVICES[@]}"; do
  echo "[degrade.sh] service=$svc requested FAULT_MODE=$ACTION"
  if docker compose exec -T "$svc" sh -c 'true' >/dev/null 2>&1; then
    echo "  note: FAULT_MODE is read once at process start, so this only"
    echo "        takes effect after restarting the container with the"
    echo "        env var set, e.g.:"
    echo "        FAULT_MODE=$ACTION docker compose up -d --no-deps $svc"
  else
    echo "  container '$svc' is not running -- set FAULT_MODE=$ACTION in"
    echo "  docker-compose.yml or .env before 'docker compose up' instead"
  fi
done
