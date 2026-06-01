from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from time import perf_counter

import structlog

from qa_note_agent.application.dtos.llm import (
    LlmGenerateRequest,
    LlmGenerateResponse,
)
from qa_note_agent.application.ports.llm import LlmClient
from qa_note_agent.infrastructure.llm.errors import OllamaClientError

logger = structlog.get_logger(__name__)


@dataclass(frozen=True, slots=True)
class OllamaLlmClient(LlmClient):
    """LLM client implementation based on local Ollama API."""

    base_url: str = "http://localhost:11434"
    model: str = "qwen2.5"
    timeout_seconds: float = 120.0
    default_options: dict[str, object] | None = None

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

        response_data = self._post_json(
            path="/api/generate",
            payload=payload,
        )

        response_text = response_data.get("response")

        if not isinstance(response_text, str):
            msg = "Ollama response does not contain string `response` field."
            raise OllamaClientError(msg)

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
            logger.exception(
                "ollama_request_failed",
                model=self.model,
                path=path,
                timeout_seconds=self.timeout_seconds,
                http_status=error.code,
                error_body_preview=error_body[:500],
                duration_ms=round((perf_counter() - started_at) * 1000),
            )
            msg = f"Ollama request failed with HTTP {error.code}: {error_body}"
            raise OllamaClientError(msg) from error
        except urllib.error.URLError as error:
            logger.exception(
                "ollama_request_failed",
                model=self.model,
                path=path,
                timeout_seconds=self.timeout_seconds,
                reason=str(error.reason),
                duration_ms=round((perf_counter() - started_at) * 1000),
            )
            msg = f"Ollama request failed: {error.reason}"
            raise OllamaClientError(msg) from error
        except TimeoutError as error:
            logger.exception(
                "ollama_request_failed",
                model=self.model,
                path=path,
                timeout_seconds=self.timeout_seconds,
                reason="timeout",
                duration_ms=round((perf_counter() - started_at) * 1000),
            )
            msg = "Ollama request timed out."
            raise OllamaClientError(msg) from error

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
