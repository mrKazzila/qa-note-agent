from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Any

from qa_note_agent.presentation.cli.commands.hello import hello_command


CLICommandFunc = Callable[..., Any]


class CLIGroup(str, Enum):
    GENERAL = "General"
    QA_NOTE = "QA Note"
    CONFIG = "Configuration"
    DEBUG = "Debug"


@dataclass(frozen=True, slots=True)
class CLICommandSpec:
    name: str
    command_func: CLICommandFunc
    help: str
    group: CLIGroup = CLIGroup.GENERAL


CLI_COMMANDS: tuple[CLICommandSpec, ...] = (
    CLICommandSpec(
        name="hello",
        command_func=hello_command,
        help="Print hello message.",
        group=CLIGroup.GENERAL,
    ),
)
