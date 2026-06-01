from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Any

from qa_note_agent.presentation.cli.commands.analyze_branch import (
    create_analyze_branch_command,
)
from qa_note_agent.presentation.cli.commands.build_qa_context import (
    create_build_qa_context_command,
)
from qa_note_agent.presentation.cli.commands.build_qa_context_chunks import (
    create_build_qa_context_chunks_command,
)
from qa_note_agent.presentation.cli.commands.generate_qa_note import (
    create_generate_qa_note_command,
)
from qa_note_agent.presentation.cli.commands.hello import hello_command
from qa_note_agent.presentation.cli.dependencies import CliContext

CLICommandFunc = Callable[..., Any]
CLICommandFactory = Callable[[CliContext], CLICommandFunc]


class CLIGroup(str, Enum):
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


def create_hello_command(_: CliContext) -> CLICommandFunc:
    """Create hello command."""
    return hello_command


CLI_COMMANDS: tuple[CLICommandSpec, ...] = (
    CLICommandSpec(
        name="hello",
        command_factory=create_hello_command,
        help="Print hello message.",
        group=CLIGroup.GENERAL,
    ),
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
        command_factory=create_build_qa_context_chunks_command,
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
