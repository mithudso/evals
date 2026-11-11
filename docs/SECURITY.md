# Security

## Trust boundaries

Operators choose suite, response, skill, fixture, and output paths. Treat file
contents as data: do not execute prompts, fixture content, YAML tags, or responses.
The tools run with the operator's filesystem permissions. They are not a sandbox
for untrusted code. No application authentication or authorization layer exists.

Replay responses and trigger queries can contain private information. Optional
embedding mode sends the skill description and query text to the configured
Ollama endpoint. Use `--lexical-only` when no embedding request is intended.

## Controls and limits

| Threat | Control or boundary |
|---|---|
| Spoofed execution evidence | Replay requires supplied responses; dry-run and legacy results remain distinct; unsupported live execution fails |
| Input tampering | Shared schema validation rejects invalid types, missing checks, invalid trigger labels, and ambiguous case IDs |
| Output path escape | Functional result filenames use a safe ASCII skill slug and output containment checks |
| Repudiation or unclear provenance | New functional summaries carry `mode` and `output_source`; legacy exports retain unknown provenance |
| Information disclosure | Operational warnings must omit raw prompts, response text, credentials, and exception bodies that may contain them |
| Resource exhaustion | Embedding timeout is three seconds with zero retries; no execution service or bulk retry worker exists |
| Privilege escalation | The toolkit does not execute arbitrary model outputs or fixture commands; caller permissions still govern local file access |
| Supply-chain changes | `uv.lock`, a pinned VCS dependency revision, SHA-pinned CI actions, and package advisory checks constrain dependency drift |

JSON parsing is not JSON Schema validation. Lexical heuristics are not a security,
semantic, compilation, or completeness proof. See [known issues](known-issues.md).

## Secrets and data handling

The application has no required secret environment variables or secret store.
Do not add credentials to suites, expected outputs, benchmark records, logs, or
versioned examples. `.env*` files are ignored except `.env.example`; the example
contains no credentials. Choose private local paths for sensitive replay outputs.
Review generated indexes before publishing them; an index must not copy private
response bodies.

## Contributor checks

- Validate input shape before grading or writing output.
- Preserve the separation between expected text, supplied responses, and live calls.
- Keep embedding model identity consistent on both sides of every comparison.
- Test malformed inputs, path boundaries, and sanitized failure logging.
- Inspect dependencies and the task-owned diff; never bypass secret protection.

## Reporting and response

Follow [security reporting guidance](../.github/SECURITY.md). No on-call service,
security response SLA, or compliance certification is claimed. For an accidental
credential exposure, stop publishing the affected output, rotate the credential
with its provider, and arrange a private report with the repository owner.

## CI dependency authentication

`OLLAMA_CLIENT_DEPLOY_KEY` is a repository Actions secret for read-only access
to the private pinned embedding client. Granting that access requires the owner
to approve the cross-repository credential. The prepared workflow writes the key
only under runner temporary storage, pins the host key, restricts the Git URL
rewrite, disables dependency caches and removes temporary key files. It does not
publish private source or run a privileged fork-PR workflow.
