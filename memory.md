# Evals memory log

## v0.1.1 - 2026-11-11

- User request:
  - Run the deep code optimizer and the repo-bootstrapper on this repo.
- Active task:
  - Implementation and local checks are complete. The owner approved the dedicated
    read-only CI deploy key, and the Actions secret is configured. GitHub CI passes
    Python 3.11, Python 3.14 and dependency audit on checkpoint `39ba3f5`. The delivery record
    [PR #1](https://github.com/mithudso/evals/pull/1) is authoritative for CI and merge state.
- Completed context:
  - Baseline commit `9eb718a` had four passing trigger transport/cosine tests.
  - The audit identified synthetic functional outputs, grader false passes,
    incomplete trigger validation, inconsistent aggregation, and missing repo tooling.
  - Regression cases were written before the runtime corrections.
  - Documentation now covers architecture, APIs, replay provenance, test strategy,
    security, integrations, known issues, and the maintained project wiki.
  - Shared contributor/agent guidance and request/workflow logs were introduced.
- Validation and audit outcome:
  - 154 tests pass on Python 3.11 and 3.14. Ruff lint/formatting, documentation
    paths/links, wheel/source build and a fresh wheel-installed CLI smoke pass.
  - Package advisory checks found no known advisories at the locked versions;
    the editable root is skipped, and this is not a source-security attestation.
  - Two optimizer iterations ran all 18 passes. The final independent gate
    retained one Medium Markdown structure dissent. A targeted token-parser
    correction fixed it with red-to-green regressions; no third blind gate ran.
  - The detailed optimizer report preserves BLIND-AUDIT-DISSENT rather than
    claiming independent-clean certification of the final targeted revision.
- Changed areas:
  - `runner/`, `benchmarks/`, `tests/`, `pyproject.toml`, `uv.lock`, and repository
    tooling/configuration are the task's implementation scope.
  - `README.md`, `docs/`, `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `CONTRIBUTING.md`,
    `CODE_OF_CONDUCT.md`, `memory.md`, and `prompts.md` form the documentation baseline.
- Constraints:
  - Preserve historical `results/`, `research/`, and `packs/` bodies. Legacy result
    provenance remains unknown; identical exports must not inflate totals.
  - Replay grades supplied responses. Dry runs grade expected text only. No live
    execution adapter, semantic judge, or JSON Schema evaluator is claimed.
  - No real model calls, embedding/index pipeline, watcher, or research refresh is
    part of this maintenance task. Tests use fakes.
- Delivery record:
  - [PR #1](https://github.com/mithudso/evals/pull/1) contains the final diff, CI checks and merge
    record. A local log does not substitute for the PR merged state.
  - See `docs/code-optimizer-report-2026-11-11.md` and
    `docs/repo-bootstrap-audit-2026-11-11.md` for evidence and applicability.
- Next steps:
  - The owner may select licensing terms. Live execution, JSON Schema evaluation
    and full service auto-remediation remain explicitly outside this CLI baseline.
  - Maintain the wiki and regenerate/check path indexes when files change.
