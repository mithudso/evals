# Testing

## Strategy and commands

Tests use synthetic suites, local temporary directories, mocked embeddings, and a
fake localhost HTTP endpoint. They do not require Ollama or call a real model.

```sh
make test
uv run --extra dev --frozen pytest tests/test_grader.py
make check
make build
```

`make check` runs Ruff lint, Ruff formatting checks, pytest, and documentation
index checks. `make build` verifies distribution packaging. The pytest config
treats `ResourceWarning` as an error so leaked test sockets do not pass quietly.

## Suites

| Test module | Scope |
|---|---|
| `tests/test_eval_runner.py` | Replay/dry-run provenance, supplied responses, malformed suites, safe output paths, CLI status, timing |
| `tests/test_grader.py` | False-pass regressions, assertion dispatch, literal extraction, negative checks, JSON and code-block structure |
| `tests/test_validation.py` | Functional/trigger shapes, required fields, ID uniqueness, safe slugs, exact boolean labels |
| `tests/test_trigger_runner.py` | Pinned model request, overrides, bounded failure fallback, cosine semantics, scoring modes, profile/suite validation, fixture cleanup |
| `tests/test_suite_validator.py` | Schema findings, missing fixtures, case-insensitive leakage checks, CLI error status |
| `tests/test_aggregate.py` | Counter validation, derived rates, duplicate records, provenance groups, Markdown boundaries, deterministic output |
| `tests/test_bootstrap_tools.py` | Index generation/drift, unsafe paths, log archives, active-editor refusal |

The fake HTTP endpoint exercises the shared embedding client's request path
without running inference. CLI tests exercise observable statuses and output;
they do not substitute expected answers for model behavior.

## Coverage target

There is no numeric line-coverage target or coverage-percentage CI gate. The
target is meaningful assertions on important and changed paths: false passes,
input boundaries, provenance, file writes, logging, CLI statuses, and resource
cleanup. Do not add assertion-free tests merely to increase line counts.

Use pytest `tmp_path` for filesystem effects and monkeypatch dependencies where
the module looks them up. Assert result evidence and observable effects, including
sanitized warning logs for fallback. Keep test server teardown in `finally` and
close the listening socket. Do not hoist mutable fixtures to shared scope.

The suite runs sequentially. Parallel test execution is not configured; isolate
shared state before introducing it. Do not replace deterministic checks with
real sleeps or remote model calls.

## CI gates and limitations

`.github/workflows/ci.yml` runs the frozen test/lint/docs/build checks on Python
3.11 and 3.14, plus a package advisory job. Inspect the actual final pushed
commit's checks before merging; a local pass does not establish remote delivery.

The toolkit does not execute agents or compile generated code. Content/behavioral
grading is lexical heuristic evidence. The suite auditor implements a subset of
its named analytical categories. Historical benchmark exports lack execution
provenance. No held-out skill-performance objective or persistent optimizer
champion is established by these tests.
