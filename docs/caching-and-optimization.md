# Caching and optimization

The runtime has no persistent application cache, vector database, CDN, or query
cache. Trigger evaluation obtains a skill-description embedding once per suite
and reuses it for each query. Query embeddings are not persisted. Lexical scoring
reuses token sets within an individual comparison.

Each invocation reads its current input files. There is no cache invalidation
protocol or stale-vector migration to run. A model change requires recalibrating
both skill/query comparisons and thresholds; do not compare mixed-model vectors.

The benchmark aggregator sorts discovered files and deduplicates identical records
before totals. It preserves distinct records and separates provenance groups.
This avoids invalid totals; it is not a claim of improved model performance.

Tests use a short polling interval for fake-server teardown and close the socket
explicitly. No test parallelism is configured. Shared mutable fixture state must
be isolated before enabling a parallel runner.

For an offline profile of local aggregation:

```sh
uv run --extra dev --frozen python -m cProfile -s cumulative \
  benchmarks/aggregate.py results /tmp/evals-profile-summary.md
```

Measure an actual bottleneck before adding caching or concurrency. No numeric
throughput or latency target is currently enforced. Optional embeddings are
bounded by the timeout/retry defaults in `runner/config.py`; choose
`--lexical-only` when network inference is not part of the intended workload.
