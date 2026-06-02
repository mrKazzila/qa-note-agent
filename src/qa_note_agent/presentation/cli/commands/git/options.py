from dataclasses import dataclass
from typing import Annotated

import typer

from qa_note_agent.presentation.cli.commands.common.options import (
    CLIOptionSpec,
    CommonOptionSpecs,
)


@dataclass
class AnalyzeBranchOptions(CommonOptionSpecs):
    show_patch = CLIOptionSpec[bool](
        annotation=Annotated[
            bool,
            typer.Option(
                "--patch",
                help="Print full unified diff patch.",
            ),
        ],
        default=False,
    )
