from __future__ import annotations


class GitCommandError(RuntimeError):
    """Raised when git command exits with non-zero status."""

    def __init__(
        self,
        command: tuple[str, ...],
        stderr: str,
        returncode: int,
    ) -> None:
        self.command = command
        self.stderr = stderr
        self.returncode = returncode

        command_text = " ".join(command)
        super().__init__(
            f"Git command failed with exit code {returncode}: {command_text}\n{stderr}",
        )
