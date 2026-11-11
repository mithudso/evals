# Installation

## Prerequisites

- Python 3.11 or newer. CI exercises Python 3.11 and 3.14.
- Git, `make`, and [uv](https://docs.astral.sh/uv/getting-started/installation/).
- Network access for the initial dependency installation.

There is no required API key, database, Node runtime, or MCP server. Ollama is
optional and is needed only when intentionally using embedding-backed scoring.

## Install and verify

```sh
git clone https://github.com/mithudso/evals.git
cd evals
make setup
make check
make build
```

The environment lives in `.venv/`. The frozen lock includes the exact
`ollama-client` Git revision used by the project. Console commands installed in
that environment are `skill-eval`, `skill-triggers`, `skill-suite-audit`, and
`skill-benchmarks`; invoke them through `uv run --frozen`.

Run the [self-contained replay example](runbooks/validation-and-replay.md) to
check a complete local workflow. Do not use an expected-answer dry run as proof
that a model executed a skill.

## Upgrade

Preserve active work before synchronizing the checkout. For a clean compatible
checkout, fetch and fast-forward the desired branch, then run `make setup` and
`make check`. Review deliberate manifest/lock changes together; do not update
dependencies implicitly while trying to reproduce a result.

## Uninstall

Stop any foreground CLI first. Removing this checkout's `.venv/` removes its
isolated Python environment; removing `dist/` removes build outputs. Keep any
needed response maps, result exports, and local input files before removing a
checkout. The toolkit installs no background daemon or database to uninstall.
