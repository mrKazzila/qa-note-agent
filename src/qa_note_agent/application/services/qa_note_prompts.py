from __future__ import annotations

from qa_note_agent.application.dtos.qa_note_context import QaNoteContextChunk

QA_NOTE_SYSTEM_PROMPT = """\
You are a senior QA analyst and software test engineer.

Your task is to analyze local Git branch changes and produce practical QA notes
for manual and regression testing.

Use only evidence from the provided Git context.
Do not invent product behavior, user-facing features, APIs, commands, screens,
settings, or integrations.

Do not perform code review.
Do not produce style, formatting, linting, documentation, naming, or readability
checklists unless the diff directly changes those behaviors, tools, or rules.

Be repository-agnostic and programming-language-agnostic.
Do not assume a specific language, framework, runtime, architecture, package
manager, test framework, deployment model, or product domain unless it is visible
in the provided Git context.

Separate internal implementation details from externally observable behavior.
A code identifier, file name, class, function, method, module, component,
package, script, test name, or directory name is not automatically a user-facing
feature.

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
- Be repository-agnostic and programming-language-agnostic.
- Do not assume a specific language, framework, runtime, package manager,
  test framework, deployment model, or product domain unless it is visible
  in the diff.
- Mention file paths when they help identify the affected area.
- Prefer concrete behavior, data flow, integration, configuration, migration,
  compatibility, error handling, security, performance, or user-visible risks
  over generic engineering advice.
- Separate internal implementation details from public behavior.
- Do not treat internal code identifiers, file names, class names, function names,
  module names, component names, package names, script names, or test names as
  user-facing features unless the diff explicitly exposes them.
- For public interfaces, mention exact names only when they are visible in the
  diff, docs, tests, routes, command registration, UI labels, config schemas,
  public API definitions, generated artifacts, or help text.
- If the public interface is unclear, describe the affected area without
  inventing names.
- Do not include code blocks.
- Do not include style, formatting, linting, naming, documentation, or readability
  checks unless directly relevant.
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
- Be repository-agnostic and programming-language-agnostic.
- Do not assume a specific language, framework, runtime, package manager,
  test framework, deployment model, or product domain unless it is visible
  in the findings.
- Be concise and specific.
- Merge duplicate findings.
- Prefer concrete manual QA scenarios over abstract validation.
- Each item in `What to test` should be actionable.
- Prioritize externally observable behavior and risk areas:
  - user-facing behavior
  - API behavior
  - CLI behavior
  - UI behavior
  - configuration behavior
  - data/storage behavior
  - migrations
  - background jobs
  - integrations
  - authentication/authorization
  - security-sensitive behavior
  - compatibility
  - error handling
  - observability/logging/metrics
  - performance-sensitive paths
- Do not treat internal code identifiers as user-facing names.
- Mention exact CLI commands, API endpoints, UI labels, settings, routes,
  events, jobs, or product names only when they are explicitly present in the
  findings.
- If the exact public interface is unclear, describe the affected behavior or
  affected area without inventing names.
- Do not include code blocks.
- Do not include "Detailed QA Checks".
- Do not include "Notes on New Files".
- Do not include explanations or meta commentary.
- Do not include style, formatting, linting, naming, documentation, or readability
  checks unless directly relevant.
- Do not mention chunks.
- Do not invent behavior that is not present in the findings.

Partial findings:

{findings_text}
"""
