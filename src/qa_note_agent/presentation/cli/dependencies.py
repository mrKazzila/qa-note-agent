from dataclasses import dataclass

from qa_note_agent.config.settings.base import Settings


@dataclass(frozen=True, slots=True)
class CliContext:
    """Dependencies available to CLI commands."""

    settings: Settings
