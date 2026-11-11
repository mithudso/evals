# Claude repository guidance

Follow [AGENTS.md](AGENTS.md) for shared ownership, task tracking, and delivery.

## Repository shape

- `runner/`: functional replay, assertion grading, trigger scoring, validation,
  and central defaults.
- `benchmarks/`: suite-quality audit and provenance-aware aggregation.
- `tests/`: synthetic behavioral tests and fake local embedding transport.
- `templates/`: starting evaluation suites; adapt their broad checks and fixtures.
- `results/`, `research/`, `packs/`: historical exports and reference bodies to preserve.
- `scripts/`: nonembedding documentation indexes and workflow-log maintenance.
- `docs/`: operating docs, generated path maps, audit reports, and the wiki.

## Commands

`make setup` installs the frozen development environment. `make check` runs lint,
format checks, tests, and doc-index checks. `make build` builds distributions.
Use `make docs-index` after documented paths or source change, and `make audit`
for package advisory checks. See [development](docs/DEVELOPMENT.md) for exact
underlying commands and single-module testing.

## Runtime architecture

Each CLI runs in a foreground Python process. Functional replay grades provided
responses; it never manufactures output from the prompt. Explicit dry runs grade
expected text and have distinct provenance. Trigger evaluation may call local
Ollama unless `--lexical-only` is set. There is no server, database, or daemon.

## Key conventions

- Require valid input and falsifiable checks; unsupported grading fails explicitly.
- Keep replay, expectation-only dry runs, and unknown legacy records separate.
- Preserve the pinned embedding model, bounded timeout, and visible fallback.
- Use fake/model-free test inputs and temporary paths for effects.
- Do not disclose credentials or private response bodies in logs or repository data.
- Preserve unrelated work; stage and ship only the owned change set.
- Update docs and path indexes together; never imply unrun checks passed.

## MCP servers

No MCP server is configured or required by the repository. See [MCP](docs/MCP.md).
Environment-provided tools do not become application dependencies.

## Workflow log rule

Append each task request to `prompts.md` using a versioned `## Prompt vN - <ISO date>`
entry. Keep the latest `memory.md` section current with active work, changed files,
completed work, and next steps. Bump the canonical patch version in
`pyproject.toml` for a delivered change set and align the memory heading.
Use `scripts/rotate_workflow_logs.py` for oversized logs; preserve archived
sections and refuse rotation while an editor swap file is present.
