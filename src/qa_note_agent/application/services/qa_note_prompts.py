from __future__ import annotations

from qa_note_agent.application.dtos.qa_note_context import QaNoteContextChunk


QA_NOTE_SYSTEM_PROMPT = """\
You are a senior QA analyst and backend engineer.

Your task is to analyze local Git branch changes and produce practical QA notes
for manual and regression testing.

Use only evidence from the provided Git context.
Do not invent product behavior.
Do not perform code review.
Do not produce style, PEP8, import, formatting, or documentation checklists
unless the diff directly changes linting, formatting, documentation tooling,
or import behavior.

Write concise, specific, test-oriented output.
"""


def build_chunk_analysis_prompt(chunk: QaNoteContextChunk) -> str:
    """Build prompt for analyzing a single diff chunk."""
    return f"""\
Analyze this Git diff context chunk.

Return findings using exactly this structure:

## Chunk summary
- ...

## Behavior changes
- ...

## QA-relevant risks
- ...

## Suggested checks
- ...

Rules:
- Focus only on this chunk.
- Mention file paths when they help identify the affected area.
- Prefer concrete behavior and integration risks over generic advice.
- Do not include code blocks.
- Do not include style, PEP8, import, formatting, or documentation checks unless directly relevant.
- Do not write final QA notes.
- If this chunk has no QA-relevant implications, say:
  - No QA-relevant implications found in this chunk.

Git context chunk:

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

Output must use exactly this structure and no extra sections:

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
- Analyze branch changes, not a single commit.
- Be concise and specific.
- Merge duplicate findings.
- Prioritize behavior, CLI behavior, Git analysis behavior, LLM integration,
  error handling, configuration, data flow, and user-visible command output.
- Do not include code blocks.
- Do not include "Detailed QA Checks".
- Do not include "Notes on New Files".
- Do not include explanations or meta commentary.
- Do not include style, PEP8, import, formatting, or documentation checks unless directly relevant.
- Do not mention chunks.
- Do not invent behavior that is not present in the findings.
- If there are no meaningful QA implications, say so directly.

Partial findings:

{findings_text}
"""
