# Onboarding

1. Read [README](../README.md) for the supported modes and provenance limits.
2. Follow [installation](INSTALLATION.md), then run `make check` from the root.
3. Run the [local replay walkthrough](runbooks/validation-and-replay.md). It uses
   synthetic response text and calls no model.
4. Read [architecture](ARCHITECTURE.md) and [components](COMPONENTS.md) before
   changing runtime behavior. Open `runner/validation.py` first for input contracts.
5. Review [testing](TESTING.md), [security](SECURITY.md), and
   [known issues](known-issues.md). Add a regression case before fixing a false pass.
6. Use [the wiki](wiki/README.md) to find commands and references. After adding or
   moving source/docs, run `make docs-index` and `make docs-check`.
7. Follow [contributing](../CONTRIBUTING.md) and the repository's delivery workflow.

Do not start Ollama, run live inference, create embeddings, or refresh the research
corpus merely to get familiar with the repository. The ordinary test suite is
designed for offline model verification with fakes.
