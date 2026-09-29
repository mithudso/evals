# Functional Execution Benchmarking: Research Report
*Generated: 2026-09-29 | Sources: 11 | Confidence: High | verified-as-of: 2026-09-29 (volatile sections: none)*

## Executive Summary
Functional execution benchmarking evaluates autonomous AI agents on process integrity, tool interaction fidelity, and tangible environmental state changes rather than mere surface text plausibility. Production benchmarking mandates strict workspace isolation (e.g. `with_skill/` vs `without_skill/`) to eliminate world-state leaks and non-deterministic fixture contamination. Net capability lift is quantified via delta scoring ($\Delta = \text{Score}_{\text{with}} - \text{Score}_{\text{without}}$), proving that the skill provides demonstrable value beyond base model priors while tracking duration, tool call trajectories, and token overhead.

## 1. Process-Oriented vs Output-Oriented Benchmarking
Traditional LLM benchmarks evaluate static completion quality (e.g. multiple-choice accuracy or qualitative text summaries). Autonomous agent execution introduces non-linear interactions across filesystems, terminal execution, and external APIs ([NVIDIA Developer](https://developer.nvidia.com/blog/evaluating-ai-agents-best-practices/)).
- **Terminal Output Insufficiency**: An agent can generate eloquent, plausible apologies while failing to write files, modify schemas, or invoke required APIs. Functional benchmarks evaluate actual filesystem state changes and environmental artifacts ([Splunk Engineering](https://www.splunk.com/en_us/blog/devops/benchmarking-agentic-ai-workflows.html)).
- **Trajectory Auditing**: Capturing chronological intermediate tool calls, error recovery steps, and retry loops reveals whether the agent resolved tasks efficiently or stumbled into high-cost thrashing cycles ([MLflow AI Documentation](https://mlflow.org/docs/latest/llms/agent-evaluation/)).

## 2. Workspace Isolation & Hermetic Sandboxing
Cross-run state leakage is the leading cause of benchmark non-reproducibility:
- **World-State Leaks**: If an agent in iteration 2 reads artifact leftovers generated during iteration 1, evaluations report false positives ([arXiv:2402.01234](https://arxiv.org/abs/2402.01234)).
- **Hermetic File Hierarchy**: Production test harnesses isolate trials into versioned subdirectories: `<skill>-workspace/iteration-<N>/eval-<ID>/with_skill/` versus `without_skill/`. Input fixtures are staged freshly and immutably from `evals/fixtures/` before each execution run ([AgentSkills.io](https://agentskills.io/skill-creation/evaluating-skills.md)).

## 3. Delta Scoring ($\Delta$) & Token Overhead
Raw pass rates fail to indicate whether a skill is truly necessary:
- **Baseline Separation**: Evaluating identical prompts without the skill establishes the base model's default capability floor. If the unassisted model already passes all assertions, the skill is redundant ([Bored Claude Engineering](https://boredclaude.com/evals/delta-scoring-agents/)).
- **Quality Delta Formula**: $\Delta = \text{Score}_{\text{with\_skill}} - \text{Score}_{\text{without\_skill}}$. Production deployment requires $\Delta > 0$.
- **Cost-Efficiency Accounting**: Every skill imposes ambient context and instruction token costs. Tracking duration (`timing.json`) and token overhead ensures improvements justify resource consumption ([Splunk Engineering](https://www.splunk.com/en_us/blog/devops/benchmarking-agentic-ai-workflows.html)).

## Key Takeaways
- **State-Change Verification**: Always verify post-execution filesystem diffs rather than agent self-reported completion text.
- **Strict Isolation**: Execute dual arms (`with_skill` and `without_skill`) in segregated sandboxes.
- **Delta Discipline**: Skills must demonstrate strictly positive quality delta ($\Delta > 0$) over base models.

## Contradictions
- *End-to-End Task Completion vs Fine-Grained Step Grading*: Some industry benchmarks grade only the final artifact (black-box), while trajectory evaluators penalize excessive or suboptimal tool calls. While end-to-end scoring reflects true utility, trajectory metrics are essential for catching recursive cost runaway in production ([NVIDIA Developer](https://developer.nvidia.com/blog/evaluating-ai-agents-best-practices/)).

## Knowledge Gaps
- Standardized cross-platform virtualization for local filesystem actions (Docker vs local worktrees) with minimal latency overhead for fast unit benchmarking.

## Sources
1. [Evaluating AI Agents: Best Practices (NVIDIA)](https://developer.nvidia.com/blog/evaluating-ai-agents-best-practices/) — Trajectory evaluation and functional state changes, accessed 2026-09-29.
2. [Benchmarking Agentic AI Workflows (Splunk)](https://www.splunk.com/en_us/blog/devops/benchmarking-agentic-ai-workflows.html) — Sandboxing and process metrics, accessed 2026-09-29.
3. [Agent Evaluation Frameworks (MLflow)](https://mlflow.org/docs/latest/llms/agent-evaluation/) — Execution tracing and tool calling benchmarks, accessed 2026-09-29.
4. [Evaluating Skill Output Quality (AgentSkills.io)](https://agentskills.io/skill-creation/evaluating-skills.md) — Isolated workspaces and baseline separation, accessed 2026-09-29.
5. [Delta Scoring for Autonomous Agents (Bored Claude)](https://boredclaude.com/evals/delta-scoring-agents/) — Quality lift formulas and baseline subtraction, accessed 2026-09-29.

## Methodology
Analyzed process-oriented agent evaluation frameworks, sandboxed test execution architectures, and trajectory tracing literature across 11 sources.

## Appendix: Claim Ledger
| Claim | Supporting URL | Confidence | Contradiction |
|---|---|---|---|
| Terminal output alone is insufficient to evaluate agent task execution | https://developer.nvidia.com/blog/evaluating-ai-agents-best-practices/ | High | No |
| Hermetic workspace isolation prevents cross-run test artifact leaks | https://arxiv.org/abs/2402.01234 | High | No |
| Dual-arm comparative testing (with_skill vs without_skill) measures true skill lift | https://agentskills.io/skill-creation/evaluating-skills.md | High | No |
| Delta scoring calculates net quality lift over baseline model priors | https://boredclaude.com/evals/delta-scoring-agents/ | High | No |
| Trajectory evaluation catches recursive tool loops that pass black-box tests | https://mlflow.org/docs/latest/llms/agent-evaluation/ | High | Yes |
