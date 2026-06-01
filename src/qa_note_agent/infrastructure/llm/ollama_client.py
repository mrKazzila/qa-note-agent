from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass

from qa_note_agent.application.dtos.llm import (
    LlmGenerateRequest,
    LlmGenerateResponse,
)
from qa_note_agent.application.ports.llm import LlmClient
from qa_note_agent.infrastructure.llm.errors import OllamaClientError


@dataclass(frozen=True, slots=True)
class OllamaLlmClient(LlmClient):
    """LLM client implementation based on local Ollama API."""

    base_url: str = "http://localhost:11434"
    # model: str = "qwen2.5-coder:7b"
    model: str = "qwen2.5"
    timeout_seconds: float = 120.0

    def generate(self, request: LlmGenerateRequest) -> LlmGenerateResponse:
        payload: dict[str, object] = {
            "model": self.model,
            "prompt": request.prompt,
            "stream": False,
            "options": {
                "temperature": 0.2,
                "num_predict": 1200,
            },
        }

        if request.system_prompt is not None:
            payload["system"] = request.system_prompt

        response_data = self._post_json(
            path="/api/generate",
            payload=payload,
        )

        response_text = response_data.get("response")

        if not isinstance(response_text, str):
            msg = "Ollama response does not contain string `response` field."
            raise OllamaClientError(msg)

        return LlmGenerateResponse(text=response_text.strip())

    def _post_json(
        self,
        *,
        path: str,
        payload: dict[str, object],
    ) -> dict[str, object]:
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
            msg = f"Ollama request failed with HTTP {error.code}: {error_body}"
            raise OllamaClientError(msg) from error
        except urllib.error.URLError as error:
            msg = f"Ollama request failed: {error.reason}"
            raise OllamaClientError(msg) from error
        except TimeoutError as error:
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

        return parsed
