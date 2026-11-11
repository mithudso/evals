# Repository bootstrap audit — 2026-11-11

Target: `mithudso/evals`, baseline `9eb718a`, package version `0.1.1`.
This is a Python CLI harness. The mdb-tam service standard is applied where its
requirements fit the actual runtime. No app server, MCP server, dashboard,
datastore, or Node toolchain exists in this repository.

## Manifest review

| Standard surface | Baseline | Result |
|---|---|---|
| Copilot, Claude, Codex and Gemini guidance | Missing | Added shared commands, conventions and ownership rules |
| Agent inventory | No repository agents | `AGENTS.md` records that no local agents are installed |
| `memory.md`, `prompts.md` | Missing | Added task context and the actual requested task |
| Workflow-log rotation and archive | Missing | Python rotator preserves archives, refuses editor swaps and concurrent edits |
| Editor, line endings, ignore rules | Minimal ignores | Added EditorConfig, attributes and Python/editor hygiene |
| Runtime and dependency policy | Python >=3.11; mutable Git dependency | Preserved runtime floor, pinned Git commit and committed `uv.lock` |
| Environment example | Missing | Documents that application source reads no environment variables directly |
| VS Code settings, extensions, debugger | Missing | Added Python/Ruff setup and expectation-check launch profile |
| Repository/editor MCP config | Missing | Explicit empty server lists; no fictional services |
| CI | Missing | Locked tests, lint, formatting, index/link drift, build, dependency audit |
| Dependabot and ownership | Missing | Weekly uv/action updates and repository-owner mapping |
| PR, issue and security-report guidance | Missing | Added templates and a private-report route without an invented SLA |
| License | No license declared | **OPEN POLICY CHOICE:** owner must choose licensing terms |
| Contribution and conduct guidance | Missing | Added project workflow and basic contributor expectations |
| Architecture, development, components | README only | Added source-grounded documentation and module/API map |
| Security, MCP and testing | Missing | Added trust boundaries, explicit MCP non-use and actual CI gates |
| Installation, onboarding, requirements | Missing | Added frozen setup, CLI examples, upgrade/uninstall and dependency notes |
| Logging, caching and integrations | Missing | Added observed behavior, fallback limits and data handling |
| External-call inventory and runbook | Missing | Added the single embedding call path, mock tests and failure behavior |
| Maintained project wiki | Missing | Added `docs/wiki/README.md` with verified entry points |
| Human and machine retrieval indexes | Missing | Added deterministic path/symbol indexes, generator and CI drift checks |
| Existing `llms.txt`, research and reference packs | Present | Preserved; their research claims were not reverified |
| Historical result JSON and summary | Present | Preserved; aggregation now labels unknown provenance and deduplicates exports |
| Hub registration | Absent | Registered repository metadata and the validation activation command |

## Applicability and remaining gaps

- Node operations registry, HTTP/MCP tool inventory and dashboard cards are
  **not applicable to this CLI architecture**. The embedding call is documented
  in `external-calls.md`; the repository does not satisfy the full five-part
  mdb-tam service auto-remediation contract. No service was invented to claim a pass.
- Semantic embeddings, corpus watchers and a separate hub dossier were not
  generated. The committed indexes contain paths, symbols and descriptions only.
  The nested crawl-repo-to-llms output-store workflow was not run.
- No license was selected. There is no invented security-response SLA, coverage
  percentage, deployment target, or performance guarantee.
- The suite auditor implements A, C, D, F, G, H, I and L checks. B, E, J and K
  remain explicitly unimplemented. JSON Schema assertions fail unsupported;
  heuristic content checks do not prove semantic correctness or code execution.
- The supplied templates are starters. The functional template references a
  missing input fixture. A dry-run or suite audit can legitimately fail on them.
- Historical result bodies have unknown execution provenance. No new model
  inference, embeddings, research, or replacement performance claims ran here.

These are explicit scope and policy limits, not hidden passing checks. The
bootstrap adds the applicable repository maintenance baseline; it does not claim
full mdb-tam service-standard compliance.

## Verification

Baseline: four tests passed; Python compilation passed. Counterexample tests were
run before code fixes. Final integrated validation and independent review are
recorded in [the optimizer report](code-optimizer-report-2026-11-11.md).

No prior audit ledger or retracted finding existed at the baseline.
