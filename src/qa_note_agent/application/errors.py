from __future__ import annotations


class QaNoteAgentError(Exception):
    """Base class for expected application errors."""

    exit_code: int = 1

    def __init__(self, message: str, *, hint: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.hint = hint
