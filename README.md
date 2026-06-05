# QA Note Agent

QA Note Agent is a local CLI tool that analyzes Git branch changes and generates practical QA notes for manual and regression testing.

The tool is designed to be repository-agnostic and programming-language-agnostic. It works with local Git repositories and focuses on Git diffs, commits, changed files, and affected behavior rather than on a specific platform such as GitHub, GitLab, or Gitea.

## What it does

QA Note Agent helps turn local Git changes into a concise QA handoff note.

It can:

- inspect changes between a base Git ref and a target ref;
- read commits, changed files, diff stats, and patches;
- split large diffs into LLM-ready chunks;
- analyze each chunk with a local LLM;
- merge partial findings into a final QA note;
- output the result to stdout or a markdown file.

Typical output includes:

- summary of changes;
- what changed;
- what to test;
- regression risks;
- edge cases;
- additional QA notes.

## Why it can be useful

This project is useful when a developer has implemented a feature, fixed a bug, or refactored code, and you need to quickly understand what should be checked by QA.

It can help with:

- preparing QA notes before handing off a branch;
- reviewing local changes before opening a pull request;
- identifying regression risks from large diffs;
- summarizing implementation changes into test-oriented language;
- working with repositories that are not hosted on GitHub/GitLab;
- using local LLMs instead of sending code to external services.

## Current approach

QA Note Agent uses a local Git-first workflow:

```text
Git branch changes
  ↓
Git CLI adapter
  ↓
Parsed domain models
  ↓
Diff chunking
  ↓
LLM map step
  ↓
LLM reduce step
  ↓
Final QA note
````

Large diffs are split into chunks before being sent to the LLM. Each chunk is analyzed separately, then the partial findings are merged into a final QA note.

This keeps the tool usable even when a branch contains many files or a large patch.

## Technologies and design

The project uses:

* Python;
* Typer for the CLI;
* Pydantic Settings for configuration;
* local Git CLI integration;
* Ollama for local LLM generation;
* Langfuse for optional tracing and observability;
* pytest for tests;
* layered architecture;
* ports and adapters;
* application use cases;
* infrastructure adapters;
* presentation renderers.

The architecture separates the main responsibilities:

```text
domain/
  Core data models.

application/
  Use cases, ports, DTOs, prompt builders, and diff chunking.

infrastructure/
  Git, LLM, and tracing adapters.

presentation/
  CLI commands and human-readable renderers.

config/
  Settings and dependency wiring.
```

## Local usage

### 1. Start Ollama

Install and run Ollama locally.

Then pull a model, for example:

```bash
ollama pull qwen2.5-coder:7b
```

Make sure Ollama is running:

```bash
ollama serve
```

By default, QA Note Agent expects Ollama at:

```text
http://localhost:11434
```

### 2. Configure environment

Create or update `env/.env`:

```env
QA_NOTE_AGENT_APP__NAME=qa_note_agent
QA_NOTE_AGENT_APP__VERSION=0.0.1
QA_NOTE_AGENT_APP__LOG_LEVEL=INFO
QA_NOTE_AGENT_APP__DEBUG=false
QA_NOTE_AGENT_APP__LOG_RENDERER=console
QA_NOTE_AGENT_APP__USE_UTC_TIMESTAMPS=true

QA_NOTE_AGENT_LLM__PROVIDER=ollama
QA_NOTE_AGENT_LLM__OLLAMA__BASE_URL=http://localhost:11434
QA_NOTE_AGENT_LLM__OLLAMA__MODEL=qwen2.5-coder:7b
QA_NOTE_AGENT_LLM__OLLAMA__TIMEOUT_SECONDS=120
QA_NOTE_AGENT_LLM__OLLAMA__TEMPERATURE=0.2
QA_NOTE_AGENT_LLM__OLLAMA__NUM_PREDICT=1200

QA_NOTE_AGENT_LANGFUSE__ENABLED=true
QA_NOTE_AGENT_LANGFUSE__PUBLIC_KEY=pk-lf-...
QA_NOTE_AGENT_LANGFUSE__SECRET_KEY=sk-lf-...
QA_NOTE_AGENT_LANGFUSE__BASE_URL=https://cloud.langfuse.com
QA_NOTE_AGENT_LANGFUSE__ENVIRONMENT=local
QA_NOTE_AGENT_LANGFUSE__SAMPLE_RATE=1.0
QA_NOTE_AGENT_LANGFUSE__DEBUG=false
```

Langfuse is optional. If `QA_NOTE_AGENT_LANGFUSE__PUBLIC_KEY` and
`QA_NOTE_AGENT_LANGFUSE__SECRET_KEY` are not set, tracing stays disabled.
When configured, the `generate` command creates a parent trace for the
QA-note run and nested generation observations for each Ollama call, then
flushes the trace before the CLI exits.

### 3. Analyze branch changes

Inspect local Git branch changes without calling the LLM:

```bash
qa-note-agent analyze-branch --repo . --base origin/main
```

Show the full patch:

```bash
qa-note-agent analyze-branch --repo . --base origin/main --patch
```

### 4. Build LLM context

Build a single LLM-ready context:

```bash
qa-note-agent build-context --repo . --base origin/main
```

Build chunked context for large diffs:

```bash
qa-note-agent build-context-chunks --repo . --base origin/main --list
```

Print a specific chunk:

```bash
qa-note-agent build-context-chunks --repo . --base origin/main --chunk 1
```

### 5. Generate QA note

Generate a QA note from local Git changes:

```bash
qa-note-agent generate --repo . --base origin/main
```

Write the result to a file:

```bash
qa-note-agent generate --repo . --base origin/main --output qa-note.md
```

Tune generation limits:

```bash
qa-note-agent generate \
  --repo . \
  --base origin/main \
  --max-chunk-chars 12000 \
  --map-temperature 0.1 \
  --reduce-temperature 0.2 \
  --map-num-predict 800 \
  --reduce-num-predict 1400
```

## Notes

QA Note Agent currently analyzes committed branch changes between a base ref and a head ref.

For example:

```bash
qa-note-agent generate --repo . --base origin/main --head HEAD
```

This compares the current branch against `origin/main` using Git merge-base logic.

If no committed changes are detected, the tool returns an empty-diff QA note without calling the LLM.
