# Logging

CLI reports go to stdout. Validation/operational failures and standard-library
logging warnings go to stderr. There is no repository-owned log daemon, central
JSONL sink, remote telemetry service, or persistent request history.

`runner/trigger_runner.py` uses a module logger for embedding request lifecycle
and fallback. Debug events mark request start/success. Warning events mark
unavailable or incompatible embeddings and lexical fallback. Result
`scoring_mode` and per-query evidence identify the scoring path independently of
whether debug logging is enabled.

Grading functions return evidence rather than writing logs. Functional summaries
record mode, output source, counters, timings, and assertion results. Their data
may be sensitive even when operational log messages are sanitized.

## Contributor rules

- Log an operation and outcome at the boundary where it occurs. Do not swallow an
  I/O failure or silently turn a missing response into a passing result.
- Use `logging.getLogger(__name__)`; choose debug for routine lifecycle detail,
  warning for explicit fallback, and error for an operation that cannot complete.
- Keep operational errors free of raw prompts, response bodies, tokens, credentials,
  and untrusted exception text. Use stable failure categories and field paths.
- Test changed error paths with pytest `caplog` or CLI capture, including the
  absence of sensitive sentinel values.
- Do not add a persistent log sink without documenting its location, access,
  retention, and redaction policy.

The [external-call inventory](external-calls.md) records the current observability
coverage and the parts of the full operations standard that remain absent.
