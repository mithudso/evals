# Components

The package contains two importable Python packages, maintenance scripts, and
versioned reference data. There is no frontend/backend service split.

## Runtime libraries and CLIs

| Module | Public interface | Inputs and outputs | Dependencies and side effects |
|---|---|---|---|
| `runner/config.py` | Named defaults such as `EMBEDDING_MODEL`, `TRIGGER_THRESHOLD` | Constant values | No I/O; defaults used by runtime modules |
| `runner/validation.py` | `validate_functional_suite`, `validate_trigger_suite`, `is_safe_skill_name` | Parsed input → field-addressed error list or boolean | Standard library; no I/O or argument mutation |
| `runner/grader.py` | `AssertionGrader.grade`, `extract_expected_patterns` | Assertion and response text → `(passed, evidence)` | Standard library, markdown-it-py and shared defaults; no model execution |
| `runner/eval_runner.py` | `run_suite`, `main`; `skill-eval` | Functional suite and supplied output map → benchmark summary | Shared grader/validation; reads JSON, prints results, optionally writes benchmark JSON |
| `runner/trigger_runner.py` | `tokenize`, `get_embedding`, `cosine_similarity`, `extract_skill_profile`, `score_query_match`, `evaluate_triggers`, `main`; `skill-triggers` | Trigger suite and skill metadata → rates, details, scoring mode and verdict | PyYAML, `ollama-client`, config/validation; optional embedding requests |
| `benchmarks/suite_validator.py` | `validate_suite`, `main`; `skill-suite-audit` | Suite JSON → schema and analytical findings | Shared validation and config; local file/fixture metadata reads |
| `benchmarks/aggregate.py` | `aggregate_results`, `main`; `skill-benchmarks` | Benchmark directory → Markdown and aggregation metadata | Local JSON reads; prints and optionally writes Markdown |

Example library use with the [runbook's suite](runbooks/validation-and-replay.md)
saved at the chosen local path:

```python
from runner.eval_runner import run_suite

summary = run_suite("path/to/suite.json", outputs={"1": "ready"})
assert summary["mode"] == "replay"
```

`run_suite(eval_file, output_dir=None, dry_run=False, execute_live=False,
outputs=None)` preserves its original positional arguments. `outputs` maps case ID
strings to response strings. Without that map, replay uses each case's
`actual_output`. `execute_live=True` is unsupported and fails explicitly.

The grader supports literal deterministic/negative checks and selected structural
checks. Content, behavioral, and generic heuristic checks use lexical signals;
they cannot establish semantic correctness. Schema checks without an implemented
schema evaluator fail explicitly. See [testing limitations](TESTING.md).

Heading and table checks use Markdown tokens. Fenced and indented examples do not
count as document headings or tables. Diff checks validate text-hunk structure
and counts; they do not apply patches or prove a change works.

## Maintenance

- `scripts/generate_doc_indexes.py` generates the path indexes and codebase map.
- `scripts/check_doc_indexes.py` validates retrieval paths and detects index drift.
- `scripts/rotate_workflow_logs.py` retains recent workflow sections, archives the
  complete original file and refuses active editor swaps or publication over a
  concurrently recreated source path.
- `Makefile` exposes the supported setup, test, lint, docs, build, and audit commands.

These are local tools. They do not create embeddings or deploy services.

## Fixtures and reference material

| Directory | Role and constraints |
|---|---|
| `templates/` | Starting suites, including deliberately broad and adversarial examples; adapt before treating them as acceptance tests |
| `inputs/` | Local input-fixture location; the template's referenced sample fixture is absent |
| `tests/` | Synthetic unit/integration tests and fake localhost embedding transport |
| `results/` | Historical benchmark exports and summary; preserve bodies and treat missing provenance as legacy unknown |
| `research/` | Existing concept reports and dossiers; this bootstrap does not reverify their research |
| `packs/` | Existing LLM context packs; preserve their source content |
| `docs/` | Maintained operating docs, wiki, generated path maps, and audit records |

Dependency flow is CLI → shared validation/config → grader or scoring helpers.
Aggregation consumes result records rather than invoking runners. Maintenance
scripts operate on repository metadata and documentation.
