# Development

## Setup

Install Python 3.11 or newer, Git, `make`, and
[uv](https://docs.astral.sh/uv/getting-started/installation/). From the repository
root, run:

```sh
make setup
make check
```

`make setup` runs `uv sync --extra dev --frozen`. It creates `.venv/` from
`uv.lock`, including the pinned Git revision of the private `ollama-client` repository.
Your Git credentials must have read access to that repository. No model or
embedding server is needed for the test suite. There is no development server,
watch mode, or live-reload process to start.

## Commands

| Purpose | Command |
|---|---|
| Full validation | `make check` |
| All tests | `make test` |
| One module's tests | `uv run --extra dev --frozen pytest tests/test_eval_runner.py` |
| Lint | `make lint` |
| Check formatting | `make format-check` |
| Apply formatting | `uv run --extra dev --frozen ruff format runner benchmarks scripts tests` |
| Regenerate path indexes | `make docs-index` |
| Check indexes | `make docs-check` |
| Build distribution files in `dist/` | `make build` |
| Package advisory audit | `make audit` |

Ruff selects `E4`, `E7`, `E9`, `F`, and `I` rules and targets Python 3.11.
There is no separate static type-checker gate. `make audit` uses
`pip-audit --skip-editable`; an unavailable advisory record for the VCS dependency
does not establish that dependency's security.

## Workflow

1. Read the source, relevant docs, and [known issues](known-issues.md).
2. Check branch/worktree ownership. Use an isolated worktree when other work is
   present. Preserve historical exports, research bodies, caches, and private data.
3. Add a regression test that distinguishes the defect from a correct result.
4. Make the smallest behavior change that resolves the issue and run its tests.
5. Update the affected documentation and regenerate indexes with `make docs-index`.
6. Run `make check` and `make build`; inspect the task-owned diff before staging.
7. Commit and push the task branch, open/update its PR, wait for final checks, and
   merge. Verify the final content on the remote default branch before recording
   the task as complete. Synchronize and remove only this task's clean merged work.

Use descriptive commit messages. Do not force-push, rewrite the default branch,
or bypass required checks. Record requests in `prompts.md` and task state in
`memory.md`; update the patch version in `pyproject.toml` per delivered change set.
Rotate oversized logs with `scripts/rotate_workflow_logs.py`; keep archives under
`docs/archive/` and do not rotate while an editor swap file is active.

## CI and dependency changes

`.github/workflows/ci.yml` runs on PRs and pushes to `main`. Python 3.11 and 3.14
jobs install the frozen development environment, run `make check`, and build.
A separate job runs the package advisory audit. GitHub Actions are pinned by
commit. Dependabot checks the uv and GitHub Actions ecosystems weekly.

CI requires the `OLLAMA_CLIENT_DEPLOY_KEY` Actions secret: a dedicated read-only
deploy key installed on the private dependency repository. The local composite
action rewrites only that dependency URL to SSH, pins the GitHub host key, and
removes the temporary key after the job. Dependency caches are disabled because
this is a public repository and the dependency source is private. A missing
secret fails clearly; fork PRs do not receive an alternative privileged workflow.
The workflow uses `pull_request`, not `pull_request_target`. Do not store a key in
the repository or substitute a broad personal token.

For an intentional dependency change, edit `pyproject.toml`, run `uv lock`, review
`uv.lock`, then rerun validation. Do not replace the pinned `ollama-client` revision
or embedding model without testing the affected behavior.

## Configuration and troubleshooting

The application reads no environment variables directly. Defaults are in
`runner/config.py`; the CLIs expose documented input and scoring options.
See [integration assumptions](integrations-and-assumptions.md) for optional Ollama
behavior and [the runbook](runbooks/validation-and-replay.md) for data formats.

- If an import fails, run `make setup` from the repository root; use `uv run`
  rather than an unrelated Python environment.
- If a replay lacks a response, supply `actual_output` or an `--outputs` mapping.
  Expected answers are not replay inputs.
- If a trigger run cannot find metadata, supply `--skill-path` explicitly.
- If embeddings are unavailable, inspect `scoring_mode`; use `--lexical-only`
  for a deliberate offline comparison.
- If indexes are stale, run `make docs-index`, review the changes, then
  `make docs-check`. Do not edit generated entries to hide missing files.
