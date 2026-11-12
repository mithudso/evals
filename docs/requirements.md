# Requirements

## Functional requirements

1. Validate suite shapes before scoring, aggregating, or writing results.
2. Grade caller-supplied response text in replay mode. Keep explicit dry-run
   expectation checks distinct, and reject unsupported live execution.
3. Return assertion evidence and fail unsupported checks explicitly.
4. Score trigger queries against parsed skill metadata, require both labelled
   classes, and identify lexical versus embedding-backed scoring.
5. Audit schema and the implemented suite-quality checks without executing fixtures.
6. Aggregate validated benchmark records deterministically, derive rates from
   counters, deduplicate identical records, and separate provenance groups.
7. Maintain discoverable documentation and path-valid retrieval indexes.

## Non-functional requirements

- Python 3.11 is the minimum supported language version; CI also exercises 3.14.
- Tests run without real model requests and clean up local server resources.
- Error paths must not expose credentials, prompts, or response bodies.
- Historical result and research bodies remain intact during maintenance.
- No latency SLO, hardware minimum beyond running Python, numeric coverage target,
  or distributed-scaling guarantee is currently defined.

## Dependencies

`pyproject.toml` defines the accepted versions; `uv.lock` records exact resolved
versions. Review both files for an intentional update.

| Dependency | Declared constraint or source | Purpose |
|---|---|---|
| Python | `>=3.11` | Runtime |
| PyYAML | `>=6` | Safe YAML frontmatter parsing |
| markdown-it-py | `>=4,<5` | Markdown structure parsing without counting fenced examples |
| `ollama-client` | Git commit `740aca7cbc5aab4941779f35f1ca17b59fe73c7f` | Embedding transport and cosine helper |
| setuptools | `>=77` build requirement | Wheel/source distribution backend |
| pytest | `>=8,<10` development extra | Behavioral test runner |
| Ruff | `>=0.16.3,<0.17` development extra | Linting and formatting |
| pip-audit | `>=2.9,<3` development extra | Package advisory checks |

The project requires ordinary local filesystem access. Optional embeddings default
to the local Ollama endpoint and pinned model described in
[integration assumptions](integrations-and-assumptions.md).
