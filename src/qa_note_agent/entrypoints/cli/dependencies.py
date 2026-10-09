from typing import assert_never

from qa_note_agent.application.ports.llm import LlmClient
from qa_note_agent.application.ports.tracing import Tracer
from qa_note_agent.application.services.diff_chunker import DiffChunker
from qa_note_agent.application.services.qa_note_generator import (
    QaNoteGenerator,
)
from qa_note_agent.application.use_cases.analyze_branch_changes import (
    AnalyzeBranchChangesUseCase,
)
from qa_note_agent.application.use_cases.build_qa_note_context import (
    BuildQaNoteContextUseCase,
)
from qa_note_agent.application.use_cases.build_qa_note_context_chunks import (
    BuildQaNoteContextChunksUseCase,
)
from qa_note_agent.application.use_cases.generate_qa_note import (
    GenerateQaNoteUseCase,
)
from qa_note_agent.config.settings.base import Settings
from qa_note_agent.infrastructure.git.cli_git_client import CliGitClient
from qa_note_agent.infrastructure.llm.ollama_client import OllamaLlmClient
from qa_note_agent.infrastructure.observability.langfuse_tracer import (
    create_tracer,
)
from qa_note_agent.presentation.cli.dependencies import CliContext


def create_cli_context(*, settings: Settings) -> CliContext:
    """Build dependencies available to CLI commands."""
    tracer = create_tracer(settings.langfuse)
    llm_client = create_llm_client(settings=settings, tracer=tracer)

    analyze_branch_changes = AnalyzeBranchChangesUseCase(
        git_client=CliGitClient(),
    )
    build_qa_note_context = BuildQaNoteContextUseCase()
    build_qa_note_context_chunks = BuildQaNoteContextChunksUseCase(
        diff_chunker=DiffChunker(),
    )
    generate_qa_note = GenerateQaNoteUseCase(
        analyze_branch_changes_use_case=analyze_branch_changes,
        build_qa_note_context_chunks_use_case=build_qa_note_context_chunks,
        qa_note_generator=QaNoteGenerator(llm_client=llm_client),
        tracer=tracer,
    )

    return CliContext(
        settings=settings,
        analyze_branch_changes_use_case=analyze_branch_changes,
        build_qa_note_context_use_case=build_qa_note_context,
        build_qa_note_context_chunks_use_case=build_qa_note_context_chunks,
        generate_qa_note_use_case=generate_qa_note,
    )


def create_llm_client(*, settings: Settings, tracer: Tracer) -> LlmClient:
    """Create configured LLM client."""
    match settings.llm.provider:
        case "ollama":
            ollama = settings.llm.ollama

            return OllamaLlmClient(
                base_url=ollama.base_url,
                model=ollama.model,
                timeout_seconds=ollama.timeout_seconds,
                default_options=ollama.default_options(),
                tracer=tracer,
            )
        case unknown:
            assert_never(unknown)
