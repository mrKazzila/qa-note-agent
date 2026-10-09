from __future__ import annotations

from pathlib import Path
from time import perf_counter

import structlog

from qa_note_agent.application.dtos.qa_note import QaNote
from qa_note_agent.application.ports.tracing import NullTracer, Tracer
from qa_note_agent.application.services.qa_note_generator import (
    QaNoteGenerator,
)
from qa_note_agent.application.services.qa_note_renderer import (
    render_empty_changes_qa_note,
)
from qa_note_agent.application.services.qa_note_sessions import (
    build_session_id,
)
from qa_note_agent.application.use_cases.analyze_branch_changes import (
    AnalyzeBranchChangesUseCase,
)
from qa_note_agent.application.use_cases.build_qa_note_context_chunks import (
    BuildQaNoteContextChunksUseCase,
)

logger = structlog.get_logger(__name__)


class GenerateQaNoteUseCase:
    """Generate QA note from local Git branch changes."""

    def __init__(
        self,
        analyze_branch_changes_use_case: AnalyzeBranchChangesUseCase,
        build_qa_note_context_chunks_use_case: BuildQaNoteContextChunksUseCase,
        qa_note_generator: QaNoteGenerator,
        tracer: Tracer = NullTracer(),
    ) -> None:
        self._analyze_branch_changes_use_case = analyze_branch_changes_use_case
        self._build_qa_note_context_chunks_use_case = (
            build_qa_note_context_chunks_use_case
        )
        self._qa_note_generator = qa_note_generator
        self._tracer = tracer

    def execute(
        self,
        *,
        repo_path: Path,
        base_ref: str,
        head_ref: str = "HEAD",
        session_id: str | None = None,
        max_chunk_chars: int = 12_000,
        map_temperature: float = 0.1,
        reduce_temperature: float = 0.2,
        map_num_predict: int = 800,
        reduce_num_predict: int = 1_400,
    ) -> QaNote:
        started_at = perf_counter()
        resolved_session_id = build_session_id(
            repo_path=repo_path,
            base_ref=base_ref,
            head_ref=head_ref,
            session_id=session_id,
        )
        base_log = logger.bind(
            repo_path=str(repo_path),
            base_ref=base_ref,
            head_ref=head_ref,
            langfuse_session_id=resolved_session_id,
        )

        try:
            with self._tracer.start_span(
                name="qa-note.generate",
                input_data={
                    "repo_path": str(repo_path),
                    "base_ref": base_ref,
                    "head_ref": head_ref,
                },
                metadata={
                    "max_chunk_chars": max_chunk_chars,
                    "map_temperature": map_temperature,
                    "reduce_temperature": reduce_temperature,
                    "map_num_predict": map_num_predict,
                    "reduce_num_predict": reduce_num_predict,
                },
                session_id=resolved_session_id,
            ) as trace:
                log = base_log.bind(
                    langfuse_trace_id=self._tracer.get_current_trace_id(),
                    langfuse_trace_url=self._tracer.get_current_trace_url(),
                )
                log.info(
                    "qa_note_generation_started",
                    max_chunk_chars=max_chunk_chars,
                    map_temperature=map_temperature,
                    reduce_temperature=reduce_temperature,
                    map_num_predict=map_num_predict,
                    reduce_num_predict=reduce_num_predict,
                )

                changes = self._analyze_branch_changes_use_case.execute(
                    repo_path=repo_path,
                    base_ref=base_ref,
                    head_ref=head_ref,
                )

                if (
                    changes.stats.files_changed == 0
                    and not changes.patch.strip()
                ):
                    qa_note = QaNote(
                        content=render_empty_changes_qa_note(
                            base_ref=base_ref,
                            head_ref=head_ref,
                        ),
                        chunks_count=0,
                        was_context_truncated=False,
                    )
                    duration_ms = round((perf_counter() - started_at) * 1000)
                    trace.update(
                        output={
                            "changed_files_count": 0,
                            "chunk_count": 0,
                            "context_truncated": False,
                            "used_llm": False,
                        },
                    )
                    log.info(
                        "qa_note_generation_completed",
                        duration_ms=duration_ms,
                        changed_files_count=0,
                        chunk_count=0,
                        context_truncated=False,
                        used_llm=False,
                    )
                    return qa_note

                chunk_set = (
                    self._build_qa_note_context_chunks_use_case.execute(
                        changes=changes,
                        max_chunk_chars=max_chunk_chars,
                    )
                )

                qa_note = self._qa_note_generator.generate(
                    chunk_set=chunk_set,
                    map_temperature=map_temperature,
                    reduce_temperature=reduce_temperature,
                    map_num_predict=map_num_predict,
                    reduce_num_predict=reduce_num_predict,
                )
                duration_ms = round((perf_counter() - started_at) * 1000)
                trace.update(
                    output={
                        "changed_files_count": changes.stats.files_changed,
                        "chunk_count": len(chunk_set.chunks),
                        "context_truncated": chunk_set.is_truncated,
                        "partial_findings_count": qa_note.chunks_count,
                        "used_llm": True,
                    },
                )
                log.info(
                    "qa_note_generation_completed",
                    duration_ms=duration_ms,
                    changed_files_count=changes.stats.files_changed,
                    chunk_count=len(chunk_set.chunks),
                    context_truncated=chunk_set.is_truncated,
                    partial_findings_count=qa_note.chunks_count,
                    used_llm=True,
                )

                return qa_note
        finally:
            self._tracer.flush()
