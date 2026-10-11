"""The trace context of the current code: the trace and span that work belongs to.

The platform's services continue the trace of every call that carries it, so the spans of a
request, in the application and in every service, nest into one trace.
"""

import secrets
from contextvars import ContextVar
from dataclasses import dataclass, replace


@dataclass(frozen=True)
class TraceContext:
    trace_id: str
    # the current span: the parent of the spans started from here
    span_id: str = ""
    session_id: str = ""
    workflow_id: str = ""
    user_id: str = ""

    def child(self, span_id: str) -> "TraceContext":
        return replace(self, span_id=span_id)


_current: ContextVar[TraceContext | None] = ContextVar("gogi_trace_context", default=None)


def current_trace() -> TraceContext | None:
    """The trace context of the current code, or None outside a trace."""
    return _current.get()


def set_trace(context: TraceContext | None):
    """Makes the context current; returns a token to restore the previous one with reset_trace."""
    return _current.set(context)


def reset_trace(token) -> None:
    _current.reset(token)


def trace_metadata() -> tuple[tuple[str, str], ...]:
    """The gRPC metadata that carries the current trace context to the platform's services."""
    context = _current.get()
    if context is None:
        return ()
    pairs = [("x-trace-id", context.trace_id)]
    for key, value in (
        ("x-span-id", context.span_id),
        ("x-session-id", context.session_id),
        ("x-workflow-id", context.workflow_id),
        ("x-user-id", context.user_id),
    ):
        if value:
            pairs.append((key, value))
    return tuple(pairs)


def new_trace_id() -> str:
    return secrets.token_hex(16)


def new_span_id() -> str:
    return secrets.token_hex(8)
