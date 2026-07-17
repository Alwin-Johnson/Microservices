import contextvars
from typing import Optional

# Context variables for distributed tracing/logging
correlation_id_ctx: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "correlation_id", default=None
)
request_id_ctx: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "request_id", default=None
)


def get_correlation_id() -> Optional[str]:
    return correlation_id_ctx.get()


def set_correlation_id(correlation_id: str) -> contextvars.Token:
    return correlation_id_ctx.set(correlation_id)


def get_request_id() -> Optional[str]:
    return request_id_ctx.get()


def set_request_id(request_id: str) -> contextvars.Token:
    return request_id_ctx.set(request_id)
