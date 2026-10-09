from __future__ import annotations

from qa_note_agent.application.dtos.llm import LlmGenerateRequest
from qa_note_agent.application.dtos.qa_note import QaNote
from qa_note_agent.application.dtos.qa_note_context import (
    QaNoteContextChunkSet,
)
from qa_note_agent.application.ports.llm import LlmClient
from qa_note_agent.application.services.qa_note_prompts import (
    QA_NOTE_SYSTEM_PROMPT,
    build_chunk_analysis_prompt,
    build_final_qa_note_prompt,
)


class QaNoteGenerator:
    """Generate a QA note by analyzing chunks and combining findings."""

    def __init__(self, llm_client: LlmClient) -> None:
        self._llm_client = llm_client

    def generate(
        self,
        *,
        chunk_set: QaNoteContextChunkSet,
        map_temperature: float,
        reduce_temperature: float,
        map_num_predict: int,
        reduce_num_predict: int,
    ) -> QaNote:
        partial_findings: list[str] = []

        for chunk in chunk_set.chunks:
            response = self._llm_client.generate(
                LlmGenerateRequest(
                    system_prompt=QA_NOTE_SYSTEM_PROMPT,
                    prompt=build_chunk_analysis_prompt(chunk=chunk),
                    options={
                        "temperature": map_temperature,
                        "num_predict": map_num_predict,
                    },
                ),
            )
            partial_findings.append(response.text)

        final_response = self._llm_client.generate(
            LlmGenerateRequest(
                system_prompt=QA_NOTE_SYSTEM_PROMPT,
                prompt=build_final_qa_note_prompt(
                    partial_findings=tuple(partial_findings),
                ),
                options={
                    "temperature": reduce_temperature,
                    "num_predict": reduce_num_predict,
                },
            ),
        )

        return QaNote(
            content=final_response.text,
            chunks_count=len(chunk_set.chunks),
            was_context_truncated=chunk_set.is_truncated,
        )
