# Integrations and assumptions

## Runtime integration

The only direct network integration is optional embedding retrieval in
`runner/trigger_runner.py:get_embedding`, through `ollama-client`.

| Setting | Default | Meaning |
|---|---|---|
| Ollama host | `http://localhost:11434` | Local embedding endpoint |
| Embedding model | `qwen3-embedding:4b` | Model used for both skill and query vectors |
| Request timeout | 3 seconds | Bound per embedding request |
| Retry rounds | 0 | No application retry loop |
| Trigger threshold | 0.28 | Scores at or above this classify as triggering |
| Positive acceptance bar | 90% | Minimum positive trigger rate |
| False-positive acceptance bar | 10% | Maximum false trigger rate |

Defaults live in `runner/config.py`. The trigger CLI accepts `--threshold` and
`--lexical-only`. The library's `get_embedding` accepts explicit host/model
arguments; the CLI does not expose host/model flags. There are no direct runtime
environment-variable reads in this repository.

Embedding requests send description/query text and receive numeric vectors. The
default local endpoint needs no repository-managed credentials. A remote endpoint
or authentication scheme must be reviewed and documented before it is introduced.
The code preserves the `[]` failure contract and reports lexical fallback through
sanitized warnings and `scoring_mode`. Different embedding models cannot be
substituted on one side of a comparison.

## External tools

- Git reads source and dependency revisions; initial dependency setup needs network.
- uv installs the frozen dependency set and builds packages.
- pytest exercises behavior; Ruff checks lint and formatting.
- pip-audit queries package advisory services. Missing advisory coverage for a VCS
  package is a limitation, not a clean security attestation.
- GitHub Actions runs CI and Dependabot maintains dependency update proposals.

## File and scoring assumptions

- Functional suites are JSON objects; trigger suites are JSON lists. Case IDs must
  select unambiguous output-map keys. See [the runbook](runbooks/validation-and-replay.md).
- Trigger metadata needs mapping-shaped YAML frontmatter with nonempty string
  name/description fields. Supply `--skill-path` when the suite layout cannot infer it.
- Fixture paths in suite audits are relative to the suite file, unless absolute.
  Missing and non-file fixtures are findings; files over 50 KiB exceed the default
  fixture-size limit.
- Content grading uses token overlap. It does not call a semantic judge or execute
  code. Thresholds are heuristics, not calibrated proof of correctness.
- Local and CI environments use the same frozen lock. There is no separate
  production environment, deployment endpoint, datastore, or cloud configuration.

See [external calls](external-calls.md) for the call inventory and current standard
coverage gaps.

## Private dependency access

The pinned `mithudso/ollama-client` source repository is private. Local setup
needs authenticated Git read access. CI expects a dedicated read-only deploy key
through the `OLLAMA_CLIENT_DEPLOY_KEY` GitHub Actions secret. The prepared
configuration does not itself grant access; the owner must approve that grant.
No private dependency source is vendored into this public repository. CI caches
are disabled for the private dependency.
