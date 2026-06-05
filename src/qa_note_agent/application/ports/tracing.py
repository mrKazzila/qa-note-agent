from __future__ import annotations

from contextlib import AbstractContextManager, contextmanager
from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(slots=True)
class TraceHandle:
    """Mutable wrapper around an active trace observation."""

    _observation: Any | None = None

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
        del (
            input_data,
            output,
            metadata,
            model,
            model_parameters,
            usage_details,
            status_message,
        )
        return


class Tracer(Protocol):
    """Tracing interface used by the application."""

    def start_span(
        self,
        *,
        name: str,
        input_data: Any | None = None,
        metadata: Any | None = None,
    ) -> AbstractContextManager[TraceHandle]: ...

    def start_generation(
        self,
        *,
        name: str,
        model: str,
        input_data: Any | None = None,
        metadata: Any | None = None,
        model_parameters: dict[str, Any] | None = None,
    ) -> AbstractContextManager[TraceHandle]: ...

    def flush(self) -> None: ...

    def get_current_trace_id(self) -> str | None: ...

    def get_current_trace_url(self) -> str | None: ...


class NullTracer:
    """No-op tracer used when Langfuse is disabled or unconfigured."""

    @contextmanager
    def start_span(
        self,
        *,
        name: str,
        input_data: Any | None = None,
        metadata: Any | None = None,
    ) -> AbstractContextManager[TraceHandle]:
        del name, input_data, metadata
        yield TraceHandle()

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
        del name, model, input_data, metadata, model_parameters
        yield TraceHandle()

    def flush(self) -> None:
        return

    def get_current_trace_id(self) -> str | None:
        return None

    def get_current_trace_url(self) -> str | None:
        return None
