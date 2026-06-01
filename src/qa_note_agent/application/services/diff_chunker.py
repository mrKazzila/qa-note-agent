from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

SplitReason = Literal["file", "hunk", "hard"]


@dataclass(frozen=True, slots=True)
class DiffChunk:
    """Single patch chunk."""

    content: str
    files: tuple[str, ...]
    split_reason: SplitReason


class DiffChunker:
    """Split unified Git diff into file-aware chunks."""

    def split(
        self,
        patch: str,
        max_chunk_chars: int,
    ) -> tuple[DiffChunk, ...]:
        """Split patch into chunks with best-effort file/hunk boundaries."""
        if max_chunk_chars <= 0:
            msg = "max_chunk_chars must be greater than 0"
            raise ValueError(msg)

        if not patch.strip():
            return ()

        chunks: list[DiffChunk] = []

        for file_patch in _split_file_patches(patch):
            file_path = _extract_file_path(file_patch)

            if len(file_patch) <= max_chunk_chars:
                chunks.append(
                    DiffChunk(
                        content=file_patch.rstrip(),
                        files=(file_path,),
                        split_reason="file",
                    ),
                )
                continue

            chunks.extend(
                _split_large_file_patch(
                    file_patch=file_patch,
                    file_path=file_path,
                    max_chunk_chars=max_chunk_chars,
                ),
            )

        return tuple(chunks)


def _split_file_patches(patch: str) -> tuple[str, ...]:
    file_patches: list[str] = []
    current_lines: list[str] = []

    for line in patch.splitlines(keepends=True):
        if line.startswith("diff --git ") and current_lines:
            file_patches.append("".join(current_lines).rstrip())
            current_lines = [line]
            continue

        current_lines.append(line)

    if current_lines:
        file_patches.append("".join(current_lines).rstrip())

    return tuple(file_patches)


def _extract_file_path(file_patch: str) -> str:
    first_line = file_patch.splitlines()[0] if file_patch.splitlines() else ""

    match = re.match(r"^diff --git a/(.+?) b/(.+)$", first_line)

    if match is None:
        return "unknown"

    return match.group(2)


def _split_large_file_patch(
    *,
    file_patch: str,
    file_path: str,
    max_chunk_chars: int,
) -> tuple[DiffChunk, ...]:
    header, hunks = _split_header_and_hunks(file_patch)

    if not hunks:
        return _hard_split_text(
            text=file_patch,
            file_path=file_path,
            max_chunk_chars=max_chunk_chars,
        )

    chunks: list[DiffChunk] = []
    current_hunks: list[str] = []

    for hunk in hunks:
        candidate = header + "".join(current_hunks) + hunk

        if len(candidate) <= max_chunk_chars:
            current_hunks.append(hunk)
            continue

        if current_hunks:
            chunks.append(
                DiffChunk(
                    content=(header + "".join(current_hunks)).rstrip(),
                    files=(file_path,),
                    split_reason="hunk",
                ),
            )
            current_hunks = []

        single_hunk_candidate = header + hunk

        if len(single_hunk_candidate) <= max_chunk_chars:
            current_hunks.append(hunk)
            continue

        chunks.extend(
            _hard_split_text(
                text=single_hunk_candidate,
                file_path=file_path,
                max_chunk_chars=max_chunk_chars,
            ),
        )

    if current_hunks:
        chunks.append(
            DiffChunk(
                content=(header + "".join(current_hunks)).rstrip(),
                files=(file_path,),
                split_reason="hunk",
            ),
        )

    return tuple(chunks)


def _split_header_and_hunks(file_patch: str) -> tuple[str, tuple[str, ...]]:
    lines = file_patch.splitlines(keepends=True)

    first_hunk_index = next(
        (index for index, line in enumerate(lines) if line.startswith("@@")),
        None,
    )

    if first_hunk_index is None:
        return file_patch, ()

    header = "".join(lines[:first_hunk_index])
    hunk_lines = lines[first_hunk_index:]

    hunks: list[str] = []
    current_hunk: list[str] = []

    for line in hunk_lines:
        if line.startswith("@@") and current_hunk:
            hunks.append("".join(current_hunk))
            current_hunk = [line]
            continue

        current_hunk.append(line)

    if current_hunk:
        hunks.append("".join(current_hunk))

    return header, tuple(hunks)


def _hard_split_text(
    *,
    text: str,
    file_path: str,
    max_chunk_chars: int,
) -> tuple[DiffChunk, ...]:
    marker = (
        f"# NOTE: this diff chunk was split inside a large hunk "
        f"for `{file_path}`.\n"
    )
    available_chars = max_chunk_chars - len(marker)

    if available_chars <= 0:
        marker = ""
        available_chars = max_chunk_chars

    chunks: list[DiffChunk] = []

    for start in range(0, len(text), available_chars):
        segment = text[start : start + available_chars].rstrip()

        if not segment:
            continue

        chunks.append(
            DiffChunk(
                content=marker + segment,
                files=(file_path,),
                split_reason="hard",
            ),
        )

    return tuple(chunks)
