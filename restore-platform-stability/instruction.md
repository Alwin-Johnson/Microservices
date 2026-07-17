# Restore Platform Stability

## Objective
Identify and fix the root cause of a cascading platform lockup in the microservices architecture, and ensure the system recovers gracefully from peak load spikes.

## Requirements
1. **Fix the root cause**: The platform must not permanently lock up during traffic spikes.
2. **Preserve exactly-once semantics**: The platform must never charge a customer twice or double-deduct inventory.
3. **Preserve performance constraints**: Do not radically increase standard HTTP timeouts, massively scale up connection pools, or remove the load-shedding concurrency limits.
4. **Ensure automatic recovery**: The system must immediately process normal traffic once peak load subsides, without requiring manual database restarts.
5. **Functional correctness**: Public APIs must remain available and correct under all standard conditions.

## Setup
The platform is located in `/workspace/environment/`.
- Run `cd /workspace/environment && ./scripts/start.sh` to boot the stack.
- Workload generator profiles are in `/workspace/environment/workload/`.

## Evaluation
Your solution will be tested against:
1. A baseline traffic profile.
2. A degraded traffic profile (fault injected).
3. A peak traffic profile (incident reproduction).
4. Strict database consistency assertions.
5. Strict anti-cheat workload verifications.
