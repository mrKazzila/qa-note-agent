from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from qa_note_agent.presentation.cli.commands.git.analyze_branch import (
    create_analyze_branch_command,
)
from qa_note_agent.presentation.cli.commands.qa_note import (
    build_qa_context_chunks,
)
from qa_note_agent.presentation.cli.commands.qa_note.build_qa_context import (
    create_build_qa_context_command,
)
from qa_note_agent.presentation.cli.commands.qa_note.generate_qa_note import (
    create_generate_qa_note_command,
)
from qa_note_agent.presentation.cli.dependencies import CliContext

CLICommandFunc = Callable[..., Any]
CLICommandFactory = Callable[[CliContext], CLICommandFunc]


class CLIGroup(StrEnum):
    GENERAL = "General"
    QA_NOTE = "QA Note"
    CONFIG = "Configuration"
    DEBUG = "Debug"
    GIT = "Git"


@dataclass(frozen=True, slots=True)
class CLICommandSpec:
    name: str
    command_factory: CLICommandFactory
    help: str
    group: CLIGroup = CLIGroup.GENERAL


CLI_COMMANDS: tuple[CLICommandSpec, ...] = (
    CLICommandSpec(
        name="analyze-branch",
        command_factory=create_analyze_branch_command,
        help="Analyze local Git branch changes.",
        group=CLIGroup.GIT,
    ),
    CLICommandSpec(
        name="build-context",
        command_factory=create_build_qa_context_command,
        help="Build LLM-ready context from local Git branch changes.",
        group=CLIGroup.QA_NOTE,
    ),
    CLICommandSpec(
        name="build-context-chunks",
        command_factory=(
            build_qa_context_chunks.create_build_qa_context_chunks_command
        ),
        help="Build chunked LLM-ready context from local Git branch changes.",
        group=CLIGroup.QA_NOTE,
    ),
    CLICommandSpec(
        name="generate",
        command_factory=create_generate_qa_note_command,
        help="Generate QA note from local Git branch changes.",
        group=CLIGroup.QA_NOTE,
    ),
)
