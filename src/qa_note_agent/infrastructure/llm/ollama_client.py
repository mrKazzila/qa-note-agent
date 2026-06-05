from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from time import perf_counter
from typing import Any

import structlog

from qa_note_agent.application.dtos.llm import (
    LlmGenerateRequest,
    LlmGenerateResponse,
)
from qa_note_agent.application.ports.llm import LlmClient
from qa_note_agent.application.ports.tracing import NullTracer, Tracer
from qa_note_agent.infrastructure.llm.errors import (
    LlmModelNotFoundError,
    OllamaClientError,
)

logger = structlog.get_logger(__name__)


@dataclass(frozen=True, slots=True)
class OllamaLlmClient(LlmClient):
    """LLM client implementation based on local Ollama API."""

    base_url: str = "http://localhost:11434"
    model: str = "qwen2.5"
    timeout_seconds: float = 120.0
    default_options: dict[str, object] | None = None
    tracer: Tracer = NullTracer()

    def generate(self, request: LlmGenerateRequest) -> LlmGenerateResponse:
        payload: dict[str, object] = {
            "model": self.model,
            "prompt": request.prompt,
            "stream": False,
        }

        if request.system_prompt is not None:
            payload["system"] = request.system_prompt

        options = self._merge_options(request.options)

        if options:
            payload["options"] = options

        with self.tracer.start_generation(
            name="ollama.generate",
            model=self.model,
            input_data={
                "system_prompt": request.system_prompt,
                "prompt": request.prompt,
            },
            metadata={
                "provider": "ollama",
                "path": "/api/generate",
            },
            model_parameters=_coerce_model_parameters(options),
        ) as generation:
            try:
                response_data = self._post_json(
                    path="/api/generate",
                    payload=payload,
                )

                response_text = response_data.get("response")

                if not isinstance(response_text, str):
                    msg = (
                        "Ollama response does not contain string "
                        "`response` field."
                    )
                    raise OllamaClientError(msg)

                generation.update(
                    output=response_text.strip(),
                    usage_details=_extract_usage_details(response_data),
                    metadata={
                        "provider": "ollama",
                        "path": "/api/generate",
                        "eval_count": response_data.get("eval_count"),
                        "prompt_eval_count": response_data.get(
                            "prompt_eval_count",
                        ),
                        "total_duration": response_data.get("total_duration"),
                    },
                )
            except Exception as error:
                generation.update(
                    metadata={
                        "provider": "ollama",
                        "path": "/api/generate",
                        "error_type": type(error).__name__,
                    },
                    status_message=str(error),
                )
                raise

        return LlmGenerateResponse(text=response_text.strip())

    def _merge_options(
        self,
        request_options: dict[str, object] | None,
    ) -> dict[str, object]:
        options: dict[str, object] = {}

        if self.default_options is not None:
            options.update(self.default_options)

        if request_options is not None:
            options.update(request_options)

        return options

    def _post_json(
        self,
        *,
        path: str,
        payload: dict[str, object],
    ) -> dict[str, object]:
        started_at = perf_counter()
        url = self.base_url.rstrip("/") + path
        body = json.dumps(payload).encode("utf-8")

        http_request = urllib.request.Request(
            url=url,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(
                http_request,
                timeout=self.timeout_seconds,
            ) as response:
                raw_body = response.read().decode("utf-8")
        except urllib.error.HTTPError as error:
            error_body = error.read().decode("utf-8", errors="replace")
            error_message = _extract_ollama_error_message(error_body)

            if error.code == 404:
                missing_model = _extract_missing_model(error_message)

                if missing_model is not None:
                    raise LlmModelNotFoundError(missing_model) from error

            logger.warning(
                "ollama_request_failed",
                model=self.model,
                path=path,
                timeout_seconds=self.timeout_seconds,
                http_status=error.code,
                error_message=error_message,
                duration_ms=round((perf_counter() - started_at) * 1000),
            )

            msg = (
                f"Ollama request failed with HTTP {error.code}: "
                f"{error_message}"
            )
            raise OllamaClientError(msg) from error
        except urllib.error.URLError as error:
            logger.warning(
                "ollama_request_failed",
                model=self.model,
                path=path,
                timeout_seconds=self.timeout_seconds,
                reason=str(error.reason),
                duration_ms=round((perf_counter() - started_at) * 1000),
            )

            msg = f"Ollama request failed: {error.reason}"
            raise OllamaClientError(
                msg,
                hint="Check that Ollama is running and reachable.",
            ) from error
        except TimeoutError as error:
            logger.warning(
                "ollama_request_failed",
                model=self.model,
                path=path,
                timeout_seconds=self.timeout_seconds,
                reason="timeout",
                duration_ms=round((perf_counter() - started_at) * 1000),
            )

            raise OllamaClientError(
                "Ollama request timed out.",
                hint=(
                    "Try increasing the Ollama timeout or using a "
                    "smaller/faster model."
                ),
            ) from error

        try:
            parsed = json.loads(raw_body)
        except json.JSONDecodeError as error:
            msg = f"Ollama returned invalid JSON: {raw_body[:500]}"
            raise OllamaClientError(msg) from error

        if not isinstance(parsed, dict):
            msg = "Ollama returned non-object JSON response."
            raise OllamaClientError(msg)

        logger.info(
            "ollama_request_completed",
            model=self.model,
            path=path,
            timeout_seconds=self.timeout_seconds,
            response_size_bytes=len(raw_body.encode("utf-8")),
            duration_ms=round((perf_counter() - started_at) * 1000),
        )

        return parsed


def _extract_ollama_error_message(error_body: str) -> str:
    try:
        parsed = json.loads(error_body)
    except json.JSONDecodeError:
        return error_body

    error_message = parsed.get("error")

    if isinstance(error_message, str):
        return error_message

    return error_body


def _extract_missing_model(error_message: str) -> str | None:
    prefix = "model '"
    suffix = "' not found"

    if not error_message.startswith(prefix):
        return None

    if not error_message.endswith(suffix):
        return None

    return error_message.removeprefix(prefix).removesuffix(suffix)


def _extract_usage_details(
    response_data: dict[str, object],
) -> dict[str, int] | None:
    prompt_tokens = response_data.get("prompt_eval_count")
    completion_tokens = response_data.get("eval_count")

    if not isinstance(prompt_tokens, int) or not isinstance(
        completion_tokens,
        int,
    ):
        return None

    return {
        "input": prompt_tokens,
        "output": completion_tokens,
        "total": prompt_tokens + completion_tokens,
    }


def _coerce_model_parameters(
    options: dict[str, object],
) -> dict[str, Any] | None:
    if not options:
        return None

    return {
        key: value
        for key, value in options.items()
        if isinstance(value, str | int | float | bool)
    }
