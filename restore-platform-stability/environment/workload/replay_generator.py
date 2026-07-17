"""
Deterministic workload replay framework using asyncio.
"""

import asyncio
import json
import random
import sys
import time
import uuid
from pathlib import Path

import httpx

HEADER_NAME = "X-Correlation-ID"


def _payload_for(template: str) -> dict:
    templates = {
        "checkout_small": {
            "customer_id": f"cust-{random.randint(1, 1000)}",
            "items": [
                {
                    "sku": f"SKU-{random.randint(1001, 1005)}",
                    "quantity": random.randint(1, 2),
                }
            ],
        }
    }
    return templates.get(template, {})


def generate_schedule(spec: dict):
    random.seed(spec.get("seed", 0))
    schedule = []

    endpoints = spec["endpoints"]
    weights = [e["weight"] for e in endpoints]

    phases = spec.get(
        "phases",
        [
            {
                "start_s": 0,
                "end_s": spec["duration_seconds"],
                "requests_per_second": spec.get("arrival", {}).get(
                    "requests_per_second", 1
                ),
            }
        ],
    )

    for phase in phases:
        start_s = phase["start_s"]
        end_s = phase["end_s"]
        rps = phase["requests_per_second"]
        duration = end_s - start_s
        total_requests = int(duration * rps)

        for i in range(total_requests):
            fire_at = start_s + (i / rps)
            ep = random.choices(endpoints, weights=weights, k=1)[0]
            payload = _payload_for(ep.get("payload_template", ""))
            url_path = ep["path"].format(
                order_id=str(uuid.UUID(int=random.getrandbits(128))),
                sku=f"SKU-{random.randint(1001, 1005)}",
            )
            schedule.append(
                {
                    "fire_at": fire_at,
                    "method": ep["method"],
                    "path": url_path,
                    "payload": payload,
                    "correlation_id": str(uuid.UUID(int=random.getrandbits(128))),
                }
            )

    schedule.sort(key=lambda x: x["fire_at"])
    return schedule


async def worker(worker_id, client, queue, results):
    while True:
        task = await queue.get()
        if task is None:
            break

        method = task["method"]
        url = task["url"]
        payload = task["payload"]
        cid = task["correlation_id"]
        scheduled_time = task["fire_at"]

        start_perf = time.perf_counter()
        status = -1
        try:
            resp = await client.request(
                method=method,
                url=url,
                json=payload or None,
                headers={HEADER_NAME: cid},
                timeout=10.0,
            )
            status = resp.status_code
        except Exception:
            status = -1

        duration_ms = round((time.perf_counter() - start_perf) * 1000, 2)

        results.append(
            {
                "t": round(scheduled_time, 3),
                "correlation_id": cid,
                "method": method,
                "path": task["path"],
                "status": status,
                "duration_ms": duration_ms,
            }
        )
        queue.task_done()


async def async_run(spec_path: str, out_path: str):
    spec = json.loads(Path(spec_path).read_text())
    base_url = spec["target_base_url"]
    concurrency = spec.get("concurrency", 5)

    schedule = generate_schedule(spec)

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    results = []

    queue = asyncio.Queue()

    limits = httpx.Limits(
        max_connections=concurrency, max_keepalive_connections=concurrency
    )
    async with httpx.AsyncClient(limits=limits) as client:
        workers = [
            asyncio.create_task(worker(i, client, queue, results))
            for i in range(concurrency)
        ]

        t0 = time.time()

        for req in schedule:
            fire_at = req["fire_at"]
            now = time.time() - t0
            if now < fire_at:
                await asyncio.sleep(fire_at - now)

            req["url"] = base_url + req["path"]
            req["actual_fire_time"] = time.time() - t0
            await queue.put(req)

        await queue.join()

        for _ in range(concurrency):
            await queue.put(None)
        await asyncio.gather(*workers)

    with open(out_path, "w") as f:
        for r in sorted(results, key=lambda x: x["t"]):
            f.write(json.dumps(r) + "\n")

    error_rate = sum(1 for r in results if r["status"] < 0 or r["status"] >= 500) / max(
        1, len(results)
    )
    print(
        f"[replay_generator] spec={spec['name']} requests={len(results)} concurrency={concurrency} error_rate={error_rate:.3f} -> {out_path}"
    )


def run(spec_path: str, out_path: str):
    asyncio.run(async_run(spec_path, out_path))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage: replay_generator.py <spec.json> <out.jsonl>")
        sys.exit(1)
    run(sys.argv[1], sys.argv[2])
