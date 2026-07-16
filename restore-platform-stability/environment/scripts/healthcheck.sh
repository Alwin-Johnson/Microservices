#!/usr/bin/env bash
set -e

cd "$(dirname "$0")/.."

# List of services in format name:port
SERVICES=(
    "gateway:8000"
    "orders:8001"
    "payments:8002"
    "inventory:8003"
)

ALL_HEALTHY=true

echo "Running health checks..."

for SERVICE in "${SERVICES[@]}"; do
    NAME="${SERVICE%%:*}"
    PORT="${SERVICE##*:}"
    
    echo -n "Checking ${NAME} on port ${PORT}... "
    
    # Try to curl the health endpoint, ignoring failure in the shell
    if curl -s -f "http://localhost:${PORT}/health" > /dev/null 2>&1; then
        echo "OK"
    else
        echo "FAIL"
        ALL_HEALTHY=false
    fi
done

if [ "$ALL_HEALTHY" = true ]; then
    echo "All services are healthy."
    exit 0
else
    echo "One or more services failed the health check."
    exit 1
fi
