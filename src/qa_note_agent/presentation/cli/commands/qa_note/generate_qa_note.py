from __future__ import annotations

import typer

from qa_note_agent.presentation.cli.commands.common.types import CLICommandFunc
from qa_note_agent.presentation.cli.commands.qa_note.options import (
    GenerateQANoteOptions as Options,
)
from qa_note_agent.presentation.cli.dependencies import CliContext
from qa_note_agent.presentation.renderers.qa_note import (
    render_qa_note_stdout,
    render_qa_note_write_summary,
)


def create_generate_qa_note_command(context: CliContext) -> CLICommandFunc:
    """Create command for generating QA note."""

    def generate_qa_note_command(
        repo_path: Options.repo_path.annotation = Options.repo_path.default,
        base_ref: Options.base_ref.annotation = Options.base_ref.default,
        head_ref: Options.head_ref.annotation = Options.head_ref.default,
        max_chunk_chars: Options.max_chunk_chars.annotation = Options.max_chunk_chars.default,
        map_temperature: Options.map_temperature.annotation = Options.map_temperature.default,
        reduce_temperature: Options.reduce_temperature.annotation = Options.reduce_temperature.default,
        map_num_predict: Options.map_num_predict.annotation = Options.map_num_predict.default,
        reduce_num_predict: Options.reduce_num_predict.annotation = Options.reduce_num_predict.default,
        output_path: Options.output_path.annotation = Options.output_path.default,
    ) -> None:
        """Generate QA note from local Git branch changes."""
        qa_note = context.generate_qa_note_use_case.execute(
            repo_path=repo_path,
            base_ref=base_ref,
            head_ref=head_ref,
            max_chunk_chars=max_chunk_chars,
            map_temperature=map_temperature,
            reduce_temperature=reduce_temperature,
            map_num_predict=map_num_predict,
            reduce_num_predict=reduce_num_predict,
        )

        if output_path is not None:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(
                data=qa_note.content + "\n", encoding="utf-8"
            )

            typer.echo(
                render_qa_note_write_summary(
                    note=qa_note,
                    output_path=output_path,
                ),
            )
            return

        typer.echo(render_qa_note_stdout(note=qa_note))

    return generate_qa_note_command
