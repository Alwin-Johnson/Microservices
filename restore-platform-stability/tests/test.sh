#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

# We must use the Python environment from the main application
PYTHON_BIN="../environment/.venv/bin/python"
if [ ! -f "$PYTHON_BIN" ]; then
    echo "Error: Python virtual environment not found in environment/.venv"
    exit 1
fi

"$PYTHON_BIN" -m pytest test_outputs.py -v
