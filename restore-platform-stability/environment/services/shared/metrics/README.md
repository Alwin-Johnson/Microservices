# shared/metrics

Owned by the observability workstream. Prometheus RED metrics
(request count, latency histogram) plus retry and connection-pool
gauges, and a `/metrics` scrape endpoint.

```python
from services.shared.metrics import flask_metrics_middleware
flask_metrics_middleware(app, "orders")
```

Scraped by `environment/monitoring/prometheus/prometheus.yml`.
No route or business-logic changes required.
