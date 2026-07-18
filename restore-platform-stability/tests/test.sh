#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

# Install uv if it is not already available
if ! command -v uv >/dev/null 2>&1; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

# Create verifier environment
uv venv .venv
source .venv/bin/activate

# Install verifier dependencies
uv pip install \
    pytest \
    httpx \
    psycopg2-binary \
    redis

# Run verifier
set +e
pytest test_outputs.py -v
EXIT_CODE=$?
set -e

# Harbor reward file
if [ "$EXIT_CODE" -eq 0 ]; then
    echo -n "1.0" > /app/reward.txt
else
    echo -n "0.0" > /app/reward.txt
fi

exit 0