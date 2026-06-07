from __future__ import annotations

from qa_note_agent.config.settings.langfuse import LangfuseSettings
from qa_note_agent.infrastructure import tracing as langfuse_tracing


class _FakeObservation:
    def __init__(self) -> None:
        self.payloads: list[dict[str, object]] = []

    def update(self, **payload: object) -> None:
        self.payloads.append(payload)


class _FailingClient:
    def flush(self) -> None:
        msg = "401 Unauthorized"
        raise RuntimeError(msg)


def test_create_tracer_returns_null_tracer_when_not_configured() -> None:
    tracer = langfuse_tracing.create_tracer(
        LangfuseSettings(
            enabled=True,
            public_key=None,
            secret_key=None,
        ),
    )

    assert isinstance(tracer, langfuse_tracing.NullTracer)


def test_sanitize_for_tracing_redacts_nested_secrets() -> None:
    payload = {
        "prompt": "api_key=abc123 token: secret-token",
        "headers": ["Bearer top-secret-token", "safe"],
        "keys": ("sk-lf-123456", "pk-lf-654321"),
    }

    sanitized = langfuse_tracing.langfuse_tracer._sanitize_for_tracing(payload)

    assert sanitized == {
        "prompt": "api_key=[REDACTED] token: [REDACTED]",
        "headers": ["[REDACTED]", "safe"],
        "keys": ("[REDACTED]", "[REDACTED]"),
    }


def test_trace_handle_update_sanitizes_payloads_before_forwarding() -> None:
    observation = _FakeObservation()
    handle = langfuse_tracing.langfuse_tracer.LangfuseTraceHandle(
        _observation=observation,
    )

    handle.update(
        input_data={"authorization": "Bearer very-secret-token"},
        output="password=hunter2",
        metadata={"public_key": "pk-lf-123"},
    )

    assert observation.payloads == [
        {
            "input": {"authorization": "[REDACTED]"},
            "output": "password=[REDACTED]",
            "metadata": {"public_key": "[REDACTED]"},
        },
    ]


def test_langfuse_tracer_flush_swallows_export_errors() -> None:
    tracer = langfuse_tracing.langfuse_tracer.LangfuseTracer(  # type: ignore[arg-type]
        client=_FailingClient(),
    )

    tracer.flush()
