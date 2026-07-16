# shared/middleware

Owned by the observability workstream. This is where the seeded
incident lives: `fault_injection.py` gates every request through a
simulated resource pool that leaks capacity under sustained load (see
the module docstring for the full mechanism). It is pure middleware --
it never imports or edits any `services/<name>` route or business
logic.

## Wiring (one-time, at app-factory in each service)

```python
from services.shared.logger import flask_logging_middleware
from services.shared.metrics import flask_metrics_middleware
from services.shared.middleware import install as install_fault_injection

flask_logging_middleware(app, "orders")
flask_metrics_middleware(app, "orders")
install_fault_injection(app, "orders")   # no-op unless FAULT_MODE=on
```

`FAULT_MODE=on` is a no-op unless the failure/hidden-failure workload
is actually driving sustained load through the affected service(s) --
baseline traffic never trips it.
