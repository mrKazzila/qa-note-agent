from __future__ import annotations

from qa_note_agent.application.dtos.qa_note_context import QaNoteContextChunk


QA_NOTE_SYSTEM_PROMPT = """\
You are a senior QA analyst and backend engineer.

Your task is to analyze Git changes and produce practical QA notes.
Be specific. Avoid generic advice. Do not invent behavior that is not supported
by commits, changed files, or patch content.
"""


def build_chunk_analysis_prompt(chunk: QaNoteContextChunk) -> str:
    """Build prompt for analyzing a single diff chunk."""
    return f"""\
Analyze this Git diff context chunk.

Return findings in this exact structure:

## Chunk summary
- ...

## Behavior changes
- ...

## Risky areas
- ...

## Suggested QA checks
- ...

## Regression risks
- ...

Rules:
- Focus on what changed in this chunk.
- Mention file paths when relevant.
- If there are no meaningful QA implications, say so.
- Do not write final release notes yet.

Chunk:

{chunk.content}
"""


def build_final_qa_note_prompt(
    *,
    partial_findings: tuple[str, ...],
) -> str:
    """Build prompt for reducing chunk findings into final QA note."""
    findings_text = "\n\n---\n\n".join(partial_findings)

    return f"""\
Create the final QA note from these partial findings.

Output in this structure:

# For QA

## Summary
- ...

## What changed
- ...

## What to test
- ...

## Regression risks
- ...

## Edge cases
- ...

## Notes
- ...

Rules:
- Be concise but specific.
- Merge duplicate findings.
- Prioritize user-visible behavior, backend behavior, data consistency,
  integrations, configuration, migrations, and tests.
- Do not mention chunks.
- Do not invent changes that are not present in the findings.

Partial findings:

{findings_text}
"""
