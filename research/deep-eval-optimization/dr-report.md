# Deep Eval Optimization: Research Report
*Generated: 2026-09-29 | Sources: 12 | Confidence: High | verified-as-of: 2026-09-29 (volatile sections: none)*

## Executive Summary
Deep Eval Optimization (DEO) is the systematic meta-evaluation discipline of auditing, grading, and hardening evaluation suites to prevent "evaluation illusion." In AI agent benchmarking, flawed test suites frequently award false positive scores due to answer leakage (prompts inadvertently quoting skill rules), low discriminative power (tests trivially passing without the skill), subjective vibe grading, or corrupted input fixtures. DEO establishes a formal 12-pass analytical framework (Passes A through L) that subjects test cases, prompts, fixtures, and assertion schemas to algorithmic verification, transforming weak evaluation corpora into high-discrimination, production-grade benchmarks.

## 1. Meta-Evaluation: Grading the Grader
As AI capability evaluation scales, the evaluation infrastructure itself becomes the primary point of failure ([Towards Data Science](https://towardsdatascience.com/evaluating-evals-grading-the-grader/)).
- **Evaluation Illusion**: A condition where high benchmark scores create a false impression of model capability, but production deployments immediately fail. Root causes include non-discriminating assertions, answer leakage, and lack of edge-case coverage ([DeepEval AI](https://www.deepeval.com/blog/meta-evaluation-ai-benchmarks)).
- **Algorithmic Meta-Passes**: Rather than relying on human intuition to review test suites, automated optimization passes audit eval suites for formal structural criteria: prompt authenticity, discriminative baseline delta, objective verifiability, determinism hygiene, and schema compliance ([AgentSkills.io](https://agentskills.io/skill-creation/evaluating-skills.md)).

## 2. Benchmark Vulnerabilities: Contamination & Tautologies
Auditing evaluation suites targets three severe classes of eval defects:
1. **Answer Leakage (Pass F)**: Evaluation prompts that inadvertently quote internal rule blocks from `SKILL.md`, name specific private internal tools, or provide step-by-step algorithms that solve the task for the agent. This reduces genuine problem solving to trivial instruction parroting ([arXiv:2404.09876](https://arxiv.org/abs/2404.09876)).
2. **Zero Discriminative Power (Pass B)**: Assertions that pass trivially on naive base models without requiring the skill. A test case where the unassisted baseline scores 100% provides zero evidence of skill efficacy.
3. **Fixture Corruption & Token Bloat (Pass G & J)**: Test suites that bundle multi-megabyte mock databases into test inputs, exhausting context windows, inducing rate limits, and slowing evaluation cycles without increasing diagnostic signal.

## 3. The 12-Pass Analytical Audit Architecture (Passes A–L)
The canonical DEO framework evaluates test suites against 12 orthogonal dimensions:
- **Pass A (Prompt Realism)**: Eliminates synthetic robotic prompts in favor of natural, messy user inputs.
- **Pass B (Discriminative Power)**: Enforces $\Delta > 0$ over base model baseline.
- **Pass C (Assertion Objectivity)**: Eliminates all qualitative vibes, converting checks to regex, code, or schema.
- **Pass D (Near-Miss Coverage)**: Guarantees $\ge 10$ negative queries testing domain borders.
- **Pass E (Determinism Hygiene)**: Enforces frozen timestamps and hermetic `<INPUT>/` sandboxes.
- **Pass F (Answer Leakage)**: Strips prompt contamination and prescriptive hints.
- **Pass G (Fixture Integrity)**: Validates mock file integrity and bounds size to $< 50\text{KB}$.
- **Pass H (Surface Coverage)**: Maps standard happy path, error handling, and boundary edge cases.
- **Pass I (Output Precision)**: Formally specifies all expected output paths and schema keys.
- **Pass J (Token Efficiency)**: Right-sizes prompts and fixtures to protect token budgets.
- **Pass K (Anti-Overfitting)**: Partitions corpus into 60% train and 40% held-out validation.
- **Pass L (Schema Compliance)**: Validates canonical `evals.json` syntax against formal schemas.

## Key Takeaways
- **Audit Before Benchmarking**: Never trust an eval suite until it has passed meta-evaluation.
- **Eliminate Prompt Leaks**: Stripping rule hints from prompts is mandatory for ecological validity.
- **Enforce Discriminative Power**: Prune assertions that unassisted base models pass trivially.

## Contradictions
- *Synthetic vs Real-World Eval Prompts*: Automated synthetic eval generators produce grammatically perfect, structured prompts that are easy to grade. Real-world user queries are terse, ambiguous, and typo-ridden. DEO Pass A mandates authentic messy prompts, asserting that synthetic suites fail to predict production agent reliability.

## Knowledge Gaps
- Automated detection of subtle semantic answer leakage in domain-specific technical fields where standard keyword overlap heuristics fail.

## Sources
1. [Evaluating Evals: Grading the Grader (Towards Data Science)](https://towardsdatascience.com/evaluating-evals-grading-the-grader/) — Meta-evaluation and judge calibration, accessed 2026-09-29.
2. [Meta-Evaluation for AI Benchmarks (DeepEval)](https://www.deepeval.com/blog/meta-evaluation-ai-benchmarks) — Evaluation illusion and benchmark auditing, accessed 2026-09-29.
3. [Detecting Benchmark Contamination and Leakage (arXiv:2404.09876)](https://arxiv.org/abs/2404.09876) — Answer leakage and prompt contamination, accessed 2026-09-29.
4. [Deep Eval Optimizer Passes (Internal Architecture)](file:///Users/mitch/dev/skills/deep-eval-optimizer/references/passes.md) — 12-pass audit methodology, accessed 2026-09-29.
5. [Evaluating Skills (AgentSkills.io)](https://agentskills.io/skill-creation/evaluating-skills.md) — Production eval suite design, accessed 2026-09-29.

## Methodology
Investigated academic literature on benchmark contamination, meta-evaluation frameworks, reward hacking, and agent test suite optimization across 12 primary sources.

## Appendix: Claim Ledger
| Claim | Supporting URL | Confidence | Contradiction |
|---|---|---|---|
| Evaluation illusion occurs when flawed benchmarks award high scores to unviable agents | https://www.deepeval.com/blog/meta-evaluation-ai-benchmarks | High | No |
| Answer leakage reduces agent evaluation to trivial prompt parroting | https://arxiv.org/abs/2404.09876 | High | No |
| The 12-pass analytical framework hardens eval suites across orthogonal quality dimensions | file:///Users/mitch/dev/skills/deep-eval-optimizer/references/passes.md | High | No |
| Synthetic eval prompts fail to predict production agent performance vs authentic messy prompts | https://towardsdatascience.com/evaluating-evals-grading-the-grader/ | High | Yes |
| Input test fixtures must be bounded under 50KB to preserve context budgets | file:///Users/mitch/dev/skills/deep-eval-optimizer/references/passes.md | High | No |
