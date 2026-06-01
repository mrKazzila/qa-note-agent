from __future__ import annotations

from pathlib import Path

from qa_note_agent.application.dtos.llm import LlmGenerateRequest
from qa_note_agent.application.dtos.qa_note import QaNote
from qa_note_agent.application.ports.llm import LlmClient
from qa_note_agent.application.services.qa_note_prompts import (
    QA_NOTE_SYSTEM_PROMPT,
    build_chunk_analysis_prompt,
    build_final_qa_note_prompt,
)
from qa_note_agent.application.use_cases.analyze_branch_changes import (
    AnalyzeBranchChangesUseCase,
)
from qa_note_agent.application.use_cases.build_qa_note_context_chunks import (
    BuildQaNoteContextChunksUseCase,
)


class GenerateQaNoteUseCase:
    """Generate QA note from local Git branch changes."""

    def __init__(
        self,
        analyze_branch_changes_use_case: AnalyzeBranchChangesUseCase,
        build_qa_note_context_chunks_use_case: BuildQaNoteContextChunksUseCase,
        llm_client: LlmClient,
    ) -> None:
        self._analyze_branch_changes_use_case = analyze_branch_changes_use_case
        self._build_qa_note_context_chunks_use_case = (
            build_qa_note_context_chunks_use_case
        )
        self._llm_client = llm_client

    def execute(
        self,
        *,
        repo_path: Path,
        base_ref: str,
        head_ref: str = "HEAD",
        max_chunk_chars: int = 12_000,
    ) -> QaNote:
        changes = self._analyze_branch_changes_use_case.execute(
            repo_path=repo_path,
            base_ref=base_ref,
            head_ref=head_ref,
        )

        chunk_set = self._build_qa_note_context_chunks_use_case.execute(
            changes=changes,
            max_chunk_chars=max_chunk_chars,
        )

        partial_findings: list[str] = []

        for chunk in chunk_set.chunks:
            prompt = build_chunk_analysis_prompt(chunk)

            response = self._llm_client.generate(
                LlmGenerateRequest(
                    system_prompt=QA_NOTE_SYSTEM_PROMPT,
                    prompt=prompt,
                )
            )

            partial_findings.append(response.text)

        final_prompt = build_final_qa_note_prompt(
            partial_findings=tuple(partial_findings),
        )

        final_response = self._llm_client.generate(
            LlmGenerateRequest(
                system_prompt=QA_NOTE_SYSTEM_PROMPT,
                prompt=final_prompt,
            )
        )

        return QaNote(
            content=final_response.text,
            chunks_count=len(chunk_set.chunks),
            was_context_truncated=chunk_set.is_truncated,
        )
