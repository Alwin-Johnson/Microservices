# shared/tracing

Owned by the observability workstream. Correlation-id generation,
extraction, and propagation used by `shared/logger` and `shared/metrics`,
and by any service making outbound calls to another service.

- `correlation.py` — context-var correlation id (`get_correlation_id`,
  `extract_or_create`).
- `traced_session.py` — `traced_session()`, a drop-in `requests.Session`
  replacement that forwards the correlation id on outbound calls.

No route or business-logic changes required to adopt this — see
`shared/middleware/README.md` for the one-line wiring at app-startup.
