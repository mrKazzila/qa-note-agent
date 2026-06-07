from __future__ import annotations

import re
from contextlib import AbstractContextManager, contextmanager
from dataclasses import dataclass
from typing import Any

import structlog
from langfuse import Langfuse, propagate_attributes

from qa_note_agent.application.ports.tracing import (
    NullTracer,
    TraceHandle,
    Tracer,
)
from qa_note_agent.config.settings.langfuse import LangfuseSettings

logger = structlog.get_logger(__name__)

_SECRET_PATTERNS = (
    re.compile(
        r"(?i)\b(api[_-]?key|secret|token|password|authorization)\b"
        r"([^\S\r\n]*[:=][^\S\r\n]*)([^\s\"'`]+)",
    ),
    re.compile(r"\b(sk|pk)-lf-[A-Za-z0-9_-]+\b"),
    re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._-]+\b"),
)
_REDACTED = "[REDACTED]"


@dataclass(slots=True)
class LangfuseTraceHandle(TraceHandle):
    def update(
        self,
        *,
        input_data: Any | None = None,
        output: Any | None = None,
        metadata: Any | None = None,
        model: str | None = None,
        model_parameters: dict[str, Any] | None = None,
        usage_details: dict[str, int] | None = None,
        status_message: str | None = None,
    ) -> None:
        if self._observation is None:
            return

        payload: dict[str, Any] = {}

        if input_data is not None:
            payload["input"] = _sanitize_for_tracing(input_data)
        if output is not None:
            payload["output"] = _sanitize_for_tracing(output)
        if metadata is not None:
            payload["metadata"] = _sanitize_for_tracing(metadata)
        if model is not None:
            payload["model"] = model
        if model_parameters is not None:
            payload["model_parameters"] = model_parameters
        if usage_details is not None:
            payload["usage_details"] = usage_details
        if status_message is not None:
            payload["status_message"] = status_message

        if payload:
            self._observation.update(**payload)


class LangfuseTracer:
    """Langfuse-backed tracing helper."""

    def __init__(self, client: Langfuse) -> None:
        self._client = client

    @contextmanager
    def start_span(
        self,
        *,
        name: str,
        input_data: Any | None = None,
        metadata: Any | None = None,
        session_id: str | None = None,
    ) -> AbstractContextManager[TraceHandle]:
        with self._client.start_as_current_observation(
            name=name,
            as_type="span",
            input=_sanitize_for_tracing(input_data),
            metadata=_sanitize_for_tracing(metadata),
        ) as observation:
            if session_id is None:
                yield LangfuseTraceHandle(observation)
                return

            with propagate_attributes(session_id=session_id):
                yield LangfuseTraceHandle(observation)

    @contextmanager
    def start_generation(
        self,
        *,
        name: str,
        model: str,
        input_data: Any | None = None,
        metadata: Any | None = None,
        model_parameters: dict[str, Any] | None = None,
    ) -> AbstractContextManager[TraceHandle]:
        with self._client.start_as_current_observation(
            name=name,
            as_type="generation",
            model=model,
            input=_sanitize_for_tracing(input_data),
            metadata=_sanitize_for_tracing(metadata),
            model_parameters=model_parameters,
        ) as observation:
            yield LangfuseTraceHandle(observation)

    def flush(self) -> None:
        try:
            self._client.flush()
        except Exception as error:
            logger.warning(
                "langfuse_flush_failed",
                error_type=type(error).__name__,
                error_message=str(error),
            )

    def get_current_trace_id(self) -> str | None:
        return self._client.get_current_trace_id()

    def get_current_trace_url(self) -> str | None:
        return self._client.get_trace_url()


def create_tracer(settings: LangfuseSettings) -> Tracer:
    """Create a Langfuse tracer or a no-op fallback."""
    if not settings.enabled:
        logger.debug("langfuse_tracing_disabled")
        return NullTracer()

    if not settings.is_configured():
        logger.info(
            "langfuse_tracing_not_configured",
            base_url=settings.base_url,
            environment=settings.environment,
        )
        return NullTracer()

    client = Langfuse(
        public_key=settings.public_key,
        secret_key=settings.secret_key,
        base_url=settings.base_url,
        environment=settings.environment,
        sample_rate=settings.sample_rate,
        debug=settings.debug,
    )

    return LangfuseTracer(client=client)


def _sanitize_for_tracing(value: Any) -> Any:
    if value is None:
        return None

    if isinstance(value, str):
        return _sanitize_string(value)

    if isinstance(value, dict):
        return {
            str(key): _sanitize_for_tracing(nested_value)
            for key, nested_value in value.items()
        }

    if isinstance(value, tuple):
        return tuple(_sanitize_for_tracing(item) for item in value)

    if isinstance(value, list):
        return [_sanitize_for_tracing(item) for item in value]

    return value


def _sanitize_string(value: str) -> str:
    redacted = value

    for pattern in _SECRET_PATTERNS:
        if pattern.pattern.startswith("(?i)\\b(api"):
            redacted = pattern.sub(r"\1\2" + _REDACTED, redacted)
            continue

        redacted = pattern.sub(_REDACTED, redacted)

    return redacted
