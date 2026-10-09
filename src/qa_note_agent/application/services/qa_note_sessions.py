from __future__ import annotations

import hashlib
import re
from pathlib import Path


def build_session_id(
    *,
    repo_path: Path,
    base_ref: str,
    head_ref: str,
    session_id: str | None,
) -> str:
    if session_id is not None and session_id.strip():
        return normalize_session_id(value=session_id)

    repo_name = repo_path.resolve().name or "repo"
    seed = f"qa-note-agent:{repo_path.resolve()}:{base_ref}:{head_ref}"
    suffix = hashlib.sha1(seed.encode("utf-8")).hexdigest()[:12]

    return normalize_session_id(
        value=f"qa-note:{repo_name}:{base_ref}:{head_ref}:{suffix}",
    )


def normalize_session_id(*, value: str) -> str:
    normalized = "".join(
        char if ord(char) < 128 else "-" for char in value.strip()
    )
    normalized = re.sub(r"\s+", "-", normalized)
    normalized = re.sub(r"[^A-Za-z0-9._:/=-]+", "-", normalized)
    normalized = normalized.strip("-") or "qa-note-session"

    return normalized[:200]
