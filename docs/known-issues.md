# Known issues and limits

| Symptom or limitation | Cause / affected area | Workaround or next step |
|---|---|---|
| `--live` cannot run a skill | No live agent adapter exists in `runner/eval_runner.py` | Supply saved responses for replay; add a tested adapter only as separately scoped work |
| A content assertion can look plausible without proving the behavior | `runner/grader.py` uses lexical heuristics for content/behavioral checks | Prefer explicit literal or structural checks; use a real execution harness for compilation, file effects, or semantic guarantees |
| A `schema` assertion cannot prove JSON Schema compliance | No JSON Schema evaluator is implemented | Use supported JSON structural checks for syntax only, or add a validated schema evaluator in a scoped change |
| The functional template reports an absent fixture | `templates/functional-eval-template.json` references `inputs/sample_input.txt`, which is not supplied relative to that suite | Replace the placeholder with an existing suite-relative fixture before using it |
| Templates can fail or produce suite-quality findings | Several checks are intentionally broad starting points | Adapt templates into concrete acceptance cases; do not treat template execution as a skill benchmark |
| Historical percentages have no confirmed execution provenance | Existing `results/` JSON exports omit mode/output-source metadata | Preserve the files; aggregate them as legacy unknown and collect new replay evidence separately |
| Four historical exports have identical copies | Top-level and per-skill result paths contain duplicate records | The aggregator deduplicates identical content; do not sum files independently |
| Suite audit does not implement every named A–L category | Implemented checks cover A, C, D, F, G, H, I, and L | Treat the audit as a partial static check, not comprehensive eval optimization |
| Package advisory coverage may omit `ollama-client` | The dependency is pinned to a Git revision rather than a normal audited release record | Review the pinned source and audit output; an omitted package is not attested clean |
| Full mdb-tam operations standard is unmet | No central JSONL error sink, remediation registry, or generated dashboard exists in this CLI toolkit | See [external calls](external-calls.md); adding those systems would need an explicit product scope |
| No semantic retrieval pipeline or watcher exists | Bootstrap maintains path/symbol indexes only | Use generated indexes; any embedding/index service must be deliberately configured and run |
| License policy is unspecified | No `LICENSE` file exists | Repository owner must select the license; this bootstrap does not infer one |

There is no numeric coverage threshold, held-out optimizer performance benchmark,
or latency SLO. The code audit and bootstrap reports record their own bounded
scope and remaining findings. Existing research under `research/` and `packs/`
has not been independently refreshed by this maintenance task.
