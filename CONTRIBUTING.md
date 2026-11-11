# Contributing

Start with [development setup](docs/DEVELOPMENT.md), [testing](docs/TESTING.md), and
[the project wiki](docs/wiki/README.md). Follow [AGENTS.md](AGENTS.md) for task
ownership and delivery.

Use synthetic fixtures and add a regression test for a behavior defect. Make
grading evidence falsifiable: a heuristic pass is not proof of model execution,
compilation, semantic correctness, or complete JSON Schema validation. Preserve
historical results and research; new benchmark evidence needs explicit provenance.

Before proposing a change, run `make check` and `make build`, update affected docs,
and review the task-owned diff. Record the commands actually run in the PR and
describe behavior changes and limitations. Never publish credentials, customer
material, private response bodies, or unrelated work.

Use the issue templates for reproducible bugs and behavior proposals. Sensitive
reports follow [security reporting guidance](.github/SECURITY.md). Community
interaction follows [the code of conduct](CODE_OF_CONDUCT.md).

No `LICENSE` file is currently present; license selection remains with the owner.
