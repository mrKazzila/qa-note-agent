from __future__ import annotations

from qa_note_agent.domain.branch_changes import (
    ChangedFile,
    ChangeStats,
    CommitInfo,
)


_COMMIT_RECORD_SEPARATOR = "\x1e"
_COMMIT_FIELD_SEPARATOR = "\x1f"


def parse_commits(raw: str) -> tuple[CommitInfo, ...]:
    """Parse custom formatted `git log` output."""
    commits: list[CommitInfo] = []

    for record in raw.split(_COMMIT_RECORD_SEPARATOR):
        record = record.strip()

        if not record:
            continue

        fields = record.split(_COMMIT_FIELD_SEPARATOR, maxsplit=5)

        if len(fields) != 6:
            continue

        sha, author_name, author_email, date, subject, body = fields

        commits.append(
            CommitInfo(
                sha=sha,
                author_name=author_name,
                author_email=author_email,
                date=date,
                subject=subject,
                body=body.strip(),
            )
        )

    return tuple(commits)


def parse_changed_files(raw: str) -> tuple[ChangedFile, ...]:
    """Parse `git diff --name-status -M` output."""
    files: list[ChangedFile] = []

    for line in raw.splitlines():
        parts = line.split("\t")

        if not parts:
            continue

        status_raw = parts[0]

        if status_raw.startswith("R") and len(parts) == 3:
            files.append(
                ChangedFile(
                    path=parts[2],
                    old_path=parts[1],
                    status="RENAMED",
                    similarity=_parse_similarity(status_raw),
                )
            )
            continue

        if status_raw.startswith("C") and len(parts) == 3:
            files.append(
                ChangedFile(
                    path=parts[2],
                    old_path=parts[1],
                    status="COPIED",
                    similarity=_parse_similarity(status_raw),
                )
            )
            continue

        if len(parts) < 2:
            continue

        files.append(
            ChangedFile(
                path=parts[1],
                status=_map_status(status_raw),
            )
        )

    return tuple(files)


def parse_numstat_summary(raw: str) -> ChangeStats:
    """Parse `git diff --numstat` output into aggregated stats."""
    files_changed = 0
    insertions = 0
    deletions = 0
    binary_files = 0

    for line in raw.splitlines():
        parts = line.split("\t", maxsplit=2)

        if len(parts) != 3:
            continue

        added_raw, deleted_raw, _path = parts
        files_changed += 1

        if added_raw == "-" or deleted_raw == "-":
            binary_files += 1
            continue

        insertions += int(added_raw)
        deletions += int(deleted_raw)

    return ChangeStats(
        files_changed=files_changed,
        insertions=insertions,
        deletions=deletions,
        binary_files=binary_files,
    )


def _parse_similarity(status_raw: str) -> int | None:
    similarity_raw = status_raw[1:]

    if not similarity_raw.isdigit():
        return None

    return int(similarity_raw)


def _map_status(status_raw: str) -> str:
    return {
        "A": "ADDED",
        "M": "MODIFIED",
        "D": "DELETED",
        "T": "TYPE_CHANGED",
        "U": "UNMERGED",
        "X": "UNKNOWN",
        "B": "BROKEN",
    }.get(status_raw, status_raw)
