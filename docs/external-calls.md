# External-call inventory

## Runtime call

| Source / operation | Target and data | Logger / tests / docs | Retry and persistence |
|---|---|---|---|
| `runner/trigger_runner.py:210`, `get_embedding` → `OllamaClient.embed` | Ollama `/api/embed`, default `http://localhost:11434`; description or query text in, numeric vector out | Module `LOGGER`; fake HTTP endpoint and scoring/fallback assertions in `tests/test_trigger_runner.py`; [integration reference](integrations-and-assumptions.md) | Three-second timeout, zero retry rounds; returns `[]` with a sanitized warning on failure; no datastore write |

The trigger CLI invokes this call unless `--lexical-only` is set. `get_embedding`
also accepts explicit host/model library arguments. No other runtime HTTP, MCP,
message-bus, or cloud SDK call is present in the application source.
Local file reads/writes occur in the runners, audit, aggregator, and maintenance
scripts; their outputs are documented in [components](COMPONENTS.md).

## Five-standard coverage

| Standard | Current state |
|---|---|
| CLI/MCP trigger | Trigger CLI exists. No general operations registry or `run/status/history/reset` command family exists |
| Centralized structured error log | Sanitized stderr warnings exist. An append-only central JSONL sink is absent |
| Error-code remediation map | Not implemented; the bounded fallback is lexical scoring, with explicit result metadata |
| Generated dashboard card | Not applicable to the current product surface; no server or dashboard is implemented |
| Datastore-landed verification | The embedding call persists no data, so read-back verification is not applicable |

This is not a full mdb-tam operations-standard pass. A Node operations service,
central remediator, or dashboard must not be invented to make this table appear
complete. Such infrastructure would be a separately scoped product change.

## Development network operations

`scripts/generate_doc_indexes.py:20` invokes Git through
`subprocess.check_output` to enumerate versioned and nonignored files. The
documentation checker uses that same inventory. This fixed-argument subprocess
reads local Git metadata, runs no reviewed source, and makes no network request.
Index generation/drift tests in `tests/test_bootstrap_tools.py` cover this path.

Frozen dependency setup fetches packages and the pinned `ollama-client` revision.
`make audit` queries package advisory services. CI/dependency update services run
on GitHub. These operations do not execute evaluation prompts or write application
results; they still require network access. Semantic indexing and file watchers
are not started by bootstrap or CI.
