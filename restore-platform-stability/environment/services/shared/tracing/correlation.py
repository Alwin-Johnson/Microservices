"""
Correlation ID utilities shared across all middleware.

Provides a context-var-based correlation id that survives across a
single request's lifetime (thread or asyncio task), so that logs and
metrics emitted from gateway -> orders -> payments -> inventory can be
joined together during an incident investigation.

Owns no business logic; safe to import from any service.
"""
import contextvars
import uuid

_correlation_id: contextvars.ContextVar[str] = contextvars.ContextVar(
    "correlation_id", default=None
)

HEADER_NAME = "X-Correlation-ID"


def new_correlation_id() -> str:
    return uuid.uuid4().hex


def set_correlation_id(value: str) -> None:
    _correlation_id.set(value)


def get_correlation_id() -> str:
    value = _correlation_id.get()
    if value is None:
        value = new_correlation_id()
        _correlation_id.set(value)
    return value


def extract_or_create(headers: dict) -> str:
    """Pull a correlation id out of inbound headers, or mint a new one
    if this is the first hop (e.g. the gateway receiving a client
    request)."""
    incoming = headers.get(HEADER_NAME) or headers.get(HEADER_NAME.lower())
    cid = incoming or new_correlation_id()
    set_correlation_id(cid)
    return cid
