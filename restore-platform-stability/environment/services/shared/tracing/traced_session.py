"""
Lightweight tracing / correlation-id propagation for outbound calls.

Wraps `requests.Session` so the correlation id set by
`services.shared.tracing.correlation` is automatically forwarded on
downstream calls (gateway -> orders -> payments -> inventory), letting
an investigator join logs across services on a single id without any
service needing to manage headers manually.
"""
import requests

from services.shared.tracing.correlation import HEADER_NAME, get_correlation_id


class TracedSession(requests.Session):
    def request(self, method, url, **kwargs):
        headers = kwargs.pop("headers", {}) or {}
        headers[HEADER_NAME] = get_correlation_id()
        kwargs["headers"] = headers
        return super().request(method, url, **kwargs)


def traced_session() -> requests.Session:
    """Drop-in replacement for `requests.Session()` in any service's
    outbound HTTP client code:

        from services.shared.tracing import traced_session
        session = traced_session()
        session.post("http://payments:8082/charge", json=payload)
    """
    return TracedSession()
