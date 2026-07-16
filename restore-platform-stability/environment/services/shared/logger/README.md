# shared/logger

Owned by the observability workstream. Structured JSON request logging,
one line per event, joinable across services on `correlation_id`.

```python
from services.shared.logger import flask_logging_middleware
flask_logging_middleware(app, "orders")
```

No route or business-logic changes required. Writes to
`environment/logs/<service>.log` (created at runtime, gitignored).
See that file's schema in the module docstring.
