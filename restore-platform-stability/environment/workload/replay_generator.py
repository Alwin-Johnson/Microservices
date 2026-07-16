"""
Workload replay driver.

Reads a workload spec (baseline.json / replay.json / hidden_replay.json)
and fires requests at the gateway according to its arrival process,
recording per-request outcomes to a JSONL results file that
scripts/replay.sh and the verifier can consume.

Usage:
    python replay_generator.py workload/replay.json results/replay_results.jsonl
"""
import json
import random
import sys
import time
import uuid
from pathlib import Path

import requests

from services.shared.tracing.correlation import HEADER_NAME


def _payload_for(template: str) -> dict:
    templates = {
        "checkout_small": {
            "order_id": str(uuid.uuid4()),
            "sku": f"sku-{random.randint(1, 500)}",
            "quantity": random.randint(1, 3),
        }
    }
    return templates.get(template, {})


def _rate_at(spec: dict, t: float) -> float:
    if "phases" in spec:
        for phase in spec["phases"]:
            if phase["start_s"] <= t < phase["end_s"]:
                return phase["requests_per_second"]
        return spec["phases"][-1]["requests_per_second"]
    return spec["arrival"]["requests_per_second"]


def run(spec_path: str, out_path: str):
    spec = json.loads(Path(spec_path).read_text())
    random.seed(spec.get("seed", 0))
    base_url = spec["target_base_url"]
    endpoints = spec["endpoints"]
    weights = [e["weight"] for e in endpoints]

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    results = []
    t0 = time.time()
    duration = spec["duration_seconds"]

    session = requests.Session()

    while time.time() - t0 < duration:
        elapsed = time.time() - t0
        rate = max(0.1, _rate_at(spec, elapsed))
        endpoint = random.choices(endpoints, weights=weights, k=1)[0]
        cid = uuid.uuid4().hex
        url = base_url + endpoint["path"].format(
            order_id=str(uuid.uuid4()), sku=f"sku-{random.randint(1, 500)}"
        )
        payload = _payload_for(endpoint.get("payload_template", ""))

        start = time.perf_counter()
        try:
            resp = session.request(
                endpoint["method"],
                url,
                json=payload or None,
                headers={HEADER_NAME: cid},
                timeout=5,
            )
            status = resp.status_code
        except requests.RequestException:
            status = -1
        duration_ms = round((time.perf_counter() - start) * 1000, 2)

        results.append(
            {
                "t": round(elapsed, 3),
                "correlation_id": cid,
                "method": endpoint["method"],
                "path": endpoint["path"],
                "status": status,
                "duration_ms": duration_ms,
            }
        )

        time.sleep(1.0 / rate)

    with open(out_path, "w") as f:
        for r in results:
            f.write(json.dumps(r) + "\n")

    error_rate = sum(1 for r in results if r["status"] < 0 or r["status"] >= 500) / max(
        1, len(results)
    )
    print(
        f"[replay_generator] spec={spec['name']} requests={len(results)} "
        f"error_rate={error_rate:.3f} -> {out_path}"
    )


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage: replay_generator.py <spec.json> <out.jsonl>")
        sys.exit(1)
    run(sys.argv[1], sys.argv[2])
