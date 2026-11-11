# Evals: skill evaluation tools

A Python CLI toolkit for grading supplied skill responses, testing trigger
boundaries, auditing evaluation suites, and aggregating benchmark exports. It
includes reusable templates and an existing research corpus for skill evaluation.

Functional replay grades responses supplied by the caller. It does not execute an
agent. A dry run grades expected answers only, and is labelled separately. Live
agent execution is not implemented. Content heuristics are not evidence that code
compiled, a model followed instructions, or a JSON Schema was satisfied.

## Quick start

Prerequisites: Python 3.11 or newer, Git, `make`, and
[uv](https://docs.astral.sh/uv/getting-started/installation/).

```sh
git clone https://github.com/mithudso/evals.git
cd evals
make setup
make check
```

To inspect a template's expectations without calling a model:

```sh
uv run --extra dev --frozen python -m runner.eval_runner \
  templates/functional-eval-template.json --dry-run
```

The example templates contain broad checks and placeholder fixtures; their checks
can fail. See [the replay walkthrough](docs/runbooks/validation-and-replay.md) for
a self-contained input and the difference between replay and expectation checks.

## Commands

| Task | Command |
|---|---|
| Grade supplied responses | `uv run --frozen skill-eval suite.json --outputs outputs.json` |
| Check trigger boundaries without embeddings | `uv run --frozen skill-triggers trigger-eval.json --skill-path /path/to/SKILL.md --lexical-only` |
| Audit a suite | `uv run --frozen skill-suite-audit suite.json` |
| Aggregate exports into a new report | `uv run --frozen skill-benchmarks results /tmp/evals-summary.md` |
| Run tests, lint, formatting, and documentation checks | `make check` |
| Build wheel and source archive | `make build` |
| Check package advisories | `make audit` |

Trigger evaluation requires both positive and negative queries. The acceptance
bars are at least 90% positive triggers and at most 10% false triggers. Embedding
mode uses the pinned `qwen3-embedding:4b` model and reports lexical fallback when
embeddings are unavailable. Use `--lexical-only` to make no embedding requests.

## Repository map

`runner/` contains grading, validation, trigger scoring, and shared defaults.
`benchmarks/` contains suite audits and aggregation. `templates/` contains starting
fixtures; `tests/` covers runtime behavior. `scripts/` maintains path indexes and
workflow logs. See [architecture](docs/ARCHITECTURE.md) and
[components](docs/COMPONENTS.md) for the APIs and data flow.

Historical `results/` exports lack response provenance. Aggregation deduplicates
identical records and reports legacy records separately from replay and dry-run
records. These historical rates do not establish measured skill performance.

## Documentation

Start with [the project wiki](docs/wiki/README.md), then use:

- [Installation](docs/INSTALLATION.md), [onboarding](docs/onboarding.md), and [development](docs/DEVELOPMENT.md).
- [Testing](docs/TESTING.md), [security](docs/SECURITY.md), and [known issues](docs/known-issues.md).
- [Requirements](docs/requirements.md), [external calls](docs/external-calls.md), and [integration assumptions](docs/integrations-and-assumptions.md).
- [Logging](docs/logging.md), [caching and optimization](docs/caching-and-optimization.md), and [MCP applicability](docs/MCP.md).
- [Codebase overview](docs/codebase-overview.md) and [machine-readable file index](docs/high_signal_file_index.json).

## Research corpus

The existing research and context packs are retained as reference material; this
bootstrap does not independently reverify their claims or refresh their research.

- [Trigger calibration](research/trigger-accuracy-and-calibration/), [functional execution](research/functional-execution-benchmarking/), and [assertion engineering](research/objective-assertion-engineering/).
- [Iteration loops](research/eval-driven-iteration-loop/) and [deep eval optimization](research/deep-eval-optimization/).
- [Depth expansion](research/depth-expansion/), [tier 3](research/tier3-expansion/), [tier 4](research/tier4-expansion/), and [context packs](packs/).

## Contributing and license

Read [contributing guidance](CONTRIBUTING.md), [agent guidance](AGENTS.md), and the
[code of conduct](CODE_OF_CONDUCT.md). Report security issues through
[the security reporting guidance](.github/SECURITY.md).

No `LICENSE` file is currently present. License selection remains open.
