import json
import os
import subprocess
from pathlib import Path
import pytest

ENV_DIR = Path(__file__).parent.parent / "environment"
WORKLOAD_DIR = ENV_DIR / "workload"
RESULTS_DIR = ENV_DIR / "results"
PYTHON_BIN = str(ENV_DIR / ".venv/bin/python")


def run_cmd(cmd: str, check=True):
    return subprocess.run(
        cmd,
        shell=True,
        env=get_env(),
        cwd=str(ENV_DIR),
        check=check,
        capture_output=True,
        text=True,
    )


def get_env():
    env = os.environ.copy()
    try:
        uid = subprocess.run(
            ["id", "-u"], capture_output=True, text=True
        ).stdout.strip()
        if os.path.exists(f"/run/user/{uid}/podman/podman.sock"):
            env["DOCKER_HOST"] = f"unix:///run/user/{uid}/podman/podman.sock"
    except Exception:
        pass
    env["PYTHONPATH"] = str(ENV_DIR)
    return env


def reset_db_and_services():
    run_cmd("cp .env.example .env")
    run_cmd("./scripts/reset.sh")
    run_cmd("cp .env.example .env")
    run_cmd("docker compose build gateway orders payments inventory")
    run_cmd("./scripts/start.sh")


def toggle_fault(active: bool):
    cmd = (
        "docker compose exec -T redis redis-cli SET fault_active 1"
        if active
        else "docker compose exec -T redis redis-cli DEL fault_active"
    )
    run_cmd(cmd)


def run_workload(spec_file: str, result_file: str):
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / result_file
    subprocess.run(
        [
            PYTHON_BIN,
            str(WORKLOAD_DIR / "replay_generator.py"),
            str(WORKLOAD_DIR / spec_file),
            str(out_path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    results = []
    with open(out_path) as f:
        for line in f:
            if line.strip():
                results.append(json.loads(line))

    if not results:
        return 0.0, 0.0

    errors = sum(1 for r in results if r["status"] < 0 or r["status"] >= 500)
    error_rate = errors / len(results)
    avg_latency = sum(r["duration_ms"] for r in results) / len(results)
    return error_rate, avg_latency


@pytest.fixture(scope="session", autouse=True)
def setup_environment():
    reset_db_and_services()
    yield


def test_baseline_workload():
    toggle_fault(False)
    error_rate, latency = run_workload("baseline.json", "baseline_results.jsonl")
    assert error_rate == 0.0, f"Baseline error rate {error_rate} > 0"
    pytest.baseline_latency = latency


def test_degraded_workload():
    toggle_fault(True)
    error_rate, latency = run_workload("baseline.json", "degraded_results.jsonl")
    assert error_rate == 0.0, f"Degraded error rate {error_rate} > 0"
    assert latency > getattr(pytest, "baseline_latency", 0), (
        "Latency did not increase during degradation (load shedding might be disabled)"
    )
    toggle_fault(False)


def test_replay_workload():
    toggle_fault(False)
    error_rate, _ = run_workload("replay.json", "replay_results.jsonl")
    assert error_rate == 0.0, f"Peak workload error rate {error_rate} > 0"


def test_replay_plus_degradation():
    toggle_fault(True)
    # We do NOT assert error rate here. The incident occurs here, and some requests may fail or hang if unfixed.
    # We just run it to trigger the incident state.
    try:
        run_workload("replay.json", "incident_results.jsonl")
    except Exception:
        pass
    toggle_fault(False)


def test_recovery():
    # If the system automatically recovered, the error rate of a subsequent baseline should be 0.0
    error_rate, _ = run_workload("baseline.json", "recovery_results.jsonl")
    assert error_rate == 0.0, (
        f"Recovery error rate {error_rate} > 0 (Platform failed to recover)"
    )


def get_db_metrics():
    def fetch_query(query: str):
        cmd = f'docker compose exec -T postgres psql -U platform_user -d platform_db -t -c "{query}"'
        res = run_cmd(cmd)
        lines = res.stdout.strip().split("\\n")
        return [line.split("|") for line in lines if line.strip()]

    orders = [row[0].strip() for row in fetch_query("SELECT status FROM orders")]
    payments = [
        {"order_id": row[0].strip(), "status": row[1].strip()}
        for row in fetch_query("SELECT order_id, status FROM payments")
    ]
    inventory = {
        row[0].strip(): int(row[1].strip())
        for row in fetch_query("SELECT sku, quantity_available FROM inventory_items")
    }
    reservations = [
        {"order_id": row[0].strip(), "status": row[1].strip()}
        for row in fetch_query("SELECT order_id, status FROM inventory_reservations")
    ]

    return {
        "orders": orders,
        "payments": payments,
        "inventory": inventory,
        "reservations": reservations,
    }


def test_exactly_once_orders():
    data = get_db_metrics()
    completed_orders = data["orders"].count("COMPLETED")
    assert completed_orders > 0, "No completed orders found"


def test_exactly_one_payments():
    data = get_db_metrics()
    completed_orders = data["orders"].count("COMPLETED")
    success_payments = sum(1 for p in data["payments"] if p["status"] == "SUCCESS")
    assert completed_orders == success_payments, (
        f"Order mismatch: {completed_orders} != {success_payments}"
    )


def test_inventory_consistency():
    data = get_db_metrics()
    for sku, qty in data["inventory"].items():
        assert qty >= 0, f"Negative inventory for {sku}: {qty}"


def test_no_duplicate_side_effects():
    data = get_db_metrics()
    from collections import Counter

    success_payment_orders = [
        p["order_id"] for p in data["payments"] if p["status"] == "SUCCESS"
    ]
    payment_counts = Counter(success_payment_orders)
    for order_id, count in payment_counts.items():
        assert count == 1, f"Duplicate SUCCESS payment found for order {order_id}"

    confirmed_reservation_orders = [
        r["order_id"] for r in data["reservations"] if r["status"] == "CONFIRMED"
    ]
    reservation_counts = Counter(confirmed_reservation_orders)
    for order_id, count in reservation_counts.items():
        assert count == 1, f"Duplicate CONFIRMED reservation found for order {order_id}"


def test_held_out_replay():
    # Ensure system works on the hidden replay workload
    toggle_fault(False)
    error_rate, _ = run_workload("hidden_replay.json", "hidden_replay_results.jsonl")
    assert error_rate == 0.0, f"Hidden replay error rate {error_rate} > 0"


def test_existing_integration_tests():
    # Verify public APIs remain broadly functional (Requirement: Functional correctness)
    script = """
import asyncio
import httpx
import sys

async def check():
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post("http://localhost:8000/checkout", json={
                "customer_id": "cust_integration",
                "items": [{"sku": "SKU-100", "quantity": 1}],
                "payment_method": "credit_card"
            }, timeout=10.0)
            if resp.status_code != 200:
                sys.exit(1)
        except Exception:
            sys.exit(1)

asyncio.run(check())
"""
    script_path = ENV_DIR / "check_functional.py"
    script_path.write_text(script)
    res = subprocess.run([PYTHON_BIN, str(script_path)], capture_output=True, text=True)
    assert res.returncode == 0, "Public API failed standard functional integration test"


def test_workload_files_unchanged():
    import hashlib

    expected_hashes = {
        "replay_generator.py": "eb4763c27bc088d0cc160c008fe0ae29",
        "baseline.json": "14eaca3f507ec81d1b3502d732b7b051",
        "replay.json": "4c1750bff4766c0ede2e9e40ee6874fe",
        "hidden_replay.json": "d5496a51dc8f73db2ec33a1154d5d438",
    }
    for filename, expected_hash in expected_hashes.items():
        filepath = WORKLOAD_DIR / filename
        assert filepath.exists(), f"Missing {filename}"
        actual_hash = hashlib.md5(filepath.read_bytes()).hexdigest()
        assert actual_hash == expected_hash, (
            f"Workload file {filename} was tampered with!"
        )
