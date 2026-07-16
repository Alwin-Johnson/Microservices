#!/usr/bin/env bash
# Orchestrates a full incident replay:
#   1. snapshot metrics ("before")
#   2. run the baseline workload to prove the platform is healthy
#   3. snapshot metrics ("during_start")
#   4. run the failure workload (replay or hidden_replay)
#   5. snapshot metrics ("after")
#
# Usage: ./scripts/replay.sh [replay|hidden_replay]
#
# Does not manage the containers themselves (see scripts/start.sh /
# healthcheck.sh for that) -- assumes the stack is already up.
set -euo pipefail

MODE="${1:-replay}"
ENV_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORKLOAD_DIR="$ENV_DIR/workload"
METRICS_DIR="$ENV_DIR/metrics"
LOG_DIR="$ENV_DIR/logs"
RESULTS_DIR="$ENV_DIR/results"

mkdir -p "$METRICS_DIR" "$LOG_DIR" "$RESULTS_DIR"

export PYTHONPATH="$ENV_DIR:${PYTHONPATH:-}"

case "$MODE" in
  replay) SPEC="$WORKLOAD_DIR/replay.json" ;;
  hidden_replay) SPEC="$WORKLOAD_DIR/hidden_replay.json" ;;
  *)
    echo "unknown mode: $MODE (expected 'replay' or 'hidden_replay')" >&2
    exit 1
    ;;
esac

_snapshot_metrics() {
  local label="$1"
  python3 - "$label" "$METRICS_DIR" <<'PY'
import sys
from pathlib import Path
import requests

label, out_dir = sys.argv[1], sys.argv[2]
services = {
    "gateway": "http://gateway:8080/metrics",
    "orders": "http://orders:8081/metrics",
    "payments": "http://payments:8082/metrics",
    "inventory": "http://inventory:8083/metrics",
}
Path(out_dir).mkdir(parents=True, exist_ok=True)
out_path = Path(out_dir) / f"{label}.prom"
with open(out_path, "w") as f:
    for name, url in services.items():
        f.write(f"# service={name} url={url}\n")
        try:
            resp = requests.get(url, timeout=5)
            f.write(resp.text)
        except requests.RequestException as exc:
            f.write(f"# scrape_failed error={exc}\n")
        f.write("\n")
print(f"[replay.sh] wrote {out_path}")
PY
}

echo "[replay.sh] snapshotting pre-incident metrics"
_snapshot_metrics "before"

echo "[replay.sh] running baseline workload (sanity check)"
python3 "$WORKLOAD_DIR/replay_generator.py" \
  "$WORKLOAD_DIR/baseline.json" "$RESULTS_DIR/baseline_results.jsonl"

echo "[replay.sh] snapshotting metrics right before failure injection"
_snapshot_metrics "during_start"

echo "[replay.sh] running failure workload: $SPEC"
python3 "$WORKLOAD_DIR/replay_generator.py" \
  "$SPEC" "$RESULTS_DIR/${MODE}_results.jsonl"

echo "[replay.sh] snapshotting post-incident metrics"
_snapshot_metrics "after"

echo "[replay.sh] capturing infra logs"
docker compose logs postgres > "$LOG_DIR/postgres.log" 2>/dev/null || true
docker compose logs redis > "$LOG_DIR/redis.log" 2>/dev/null || true

echo "[replay.sh] done. logs=$LOG_DIR metrics=$METRICS_DIR raw_results=$RESULTS_DIR"
