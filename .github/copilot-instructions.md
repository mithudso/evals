## Default Execution Strategy

- Read the relevant source and repository guidance before editing.
- Run the applicable tests after each behavior change and `make check` before delivery.
- Use verified commands and paths. Record unknowns instead of inventing them.
- Record task requests in `prompts.md` and completion context in `memory.md`.
  Update the patch version in `pyproject.toml` for a delivered change set.

## Build, Test, and Validation Commands

Run `make setup`, `make check`, and `make build` from the repository root.
Use `make docs-index` after changing source or documentation, then `make docs-check`.
Use `make audit` for the package advisory check. See [development](../docs/DEVELOPMENT.md).

## High-level Architecture

`runner/` grades supplied responses and classifies trigger queries. `benchmarks/`
audits suite inputs and aggregates results by provenance. `scripts/` maintains
nonembedding retrieval indexes and rotates workflow logs. There is no server.

## Key Conventions

- Never fabricate a model response or treat expected answers as observed execution.
- Preserve the distinction between replay, expectation-only dry runs, and legacy results.
- Mock embeddings in tests; keep the model pin in `runner/config.py` consistent.
- Validate JSON and YAML shapes before scoring. Reject unsupported checks explicitly.
- Preserve historical `results/`, `research/`, and `packs/` content.
- Keep credentials and private prompts out of versioned files and logs.
- Use an isolated worktree when other work is present; stage only task-owned changes.
- Validate and deliver completed changes through a passing PR to the default branch.

See [agent guidance](../AGENTS.md) and [the project wiki](../docs/wiki/README.md).
