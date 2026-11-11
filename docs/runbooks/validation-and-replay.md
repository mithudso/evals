# Validate and replay a suite

## Preconditions

Run `make setup` from the repository root. Use synthetic or approved local input
only. This procedure grades supplied text and makes no model or embedding calls.

## Self-contained replay

Create temporary inputs so existing result files stay intact:

```sh
evals_demo_dir=$(mktemp -d)
cat > "$evals_demo_dir/suite.json" <<'JSON'
{
  "skill_name": "replay-demo",
  "evals": [
    {
      "id": 1,
      "name": "literal-response",
      "prompt": "Return the readiness marker.",
      "expected_output": "ready",
      "assertions": [
        {"name": "readiness", "type": "deterministic", "check": "contains `ready`"}
      ]
    }
  ]
}
JSON
cat > "$evals_demo_dir/outputs.json" <<'JSON'
{"1": "ready"}
JSON
uv run --frozen skill-eval "$evals_demo_dir/suite.json" \
  --outputs "$evals_demo_dir/outputs.json" --output-dir "$evals_demo_dir/results"
```

The output-map key is the string form of the case ID. A case may instead provide
`actual_output` directly. Never populate replay output by copying the expected
answer merely to improve a benchmark; the example uses a synthetic marker to show
the input contract, not to measure a skill.

## Verification

Inspect the new `replay-demo-benchmark.json` in the printed temporary results
directory. Its provenance is `mode: replay` and `output_source: provided-output`.
A successful literal assertion shows that the supplied text contains the marker;
it does not prove where that text came from or that a model executed anything.

To check expectations only, run:

```sh
uv run --frozen skill-eval "$evals_demo_dir/suite.json" --dry-run
```

This grades `expected_output` verbatim and reports `mode: dry-run` with
`output_source: expected_output`. It is not included in replay aggregate totals.
`--live` fails explicitly because no live execution adapter exists.

Audit a suite separately with `uv run --frozen skill-suite-audit PATH`. A one-case
demonstration like this produces a minimum-case coverage finding; the auditor's
nonzero status is expected. Adapt real suites to cover the required boundaries.

## Trigger and aggregation procedures

```sh
uv run --frozen skill-triggers templates/trigger-eval-template.json \
  --skill-path /path/to/your/SKILL.md --lexical-only
uv run --frozen skill-benchmarks results /tmp/evals-summary.md
```

Replace the skill path with an existing file that has valid YAML frontmatter.
Use both positive and negative labelled queries. Inspect the actual scoring mode
and failures; template queries are placeholders and do not guarantee a pass.
The aggregate report separates replay, dry-run, and legacy unknown records and
deduplicates identical exports. Preserve historical `results/` files.

## Failure, rollback, and escalation

- For schema errors, fix the named field; do not remove assertions to get a pass.
- For missing response text, supply observed output rather than enabling dry-run
  as a substitute for replay.
- For unsupported checks, choose an implemented check or arrange a scoped grader
  change with a regression test.
- For a code regression, revert the task's merged change through the normal PR
  workflow and rerun `make check`; preserve unrelated active work.
- Report a reproducible defect with a synthetic fixture through GitHub. Use the
  [private security route](../../.github/SECURITY.md) for sensitive issues.
