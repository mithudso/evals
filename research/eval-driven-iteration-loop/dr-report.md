# Eval-Driven Iteration Loop: Research Report
*Generated: 2026-09-29 | Sources: 12 | Confidence: High | verified-as-of: 2026-09-29 (volatile sections: none)*

## Executive Summary
Eval-Driven Development (EDD) establishes quantitative evaluations as the primary specification, regression gate, and architectural feedback loop for AI agent capabilities. Borrowing principles from Test-Driven Development (TDD), EDD enforces a closed five-phase iteration loop: baseline auditing, sandboxed execution, automated grading, root-cause diagnosis, and minimal instruction diffing. To prevent production degradation, new skill revisions are governed by champion-challenger promotion gating: a challenger version is released only if it achieves a strictly positive quality lift ($\Delta > 0$) without inducing any regressions on a frozen golden test suite.

## 1. Eval-Driven Development (EDD) Foundations
Rather than editing agent system prompts based on ad-hoc conversational feedback or "vibes," engineering teams utilize formal evaluations as executable contracts ([DeepEval](https://www.deepeval.com/blog/eval-driven-development-ai-agents)).
- **Evaluations as Specifications**: Test cases in `evals/evals.json` define the boundary of acceptable behavior before instruction code is authored ([Braintrust AI](https://www.braintrust.dev/blog/eval-driven-development/)).
- **Closed-Loop Feedback**: Benchmark outputs are ingested directly into automated optimization harnesses (e.g. `skill-optimizer` and `deep-eval-optimizer`), converting failed assertion logs into targeted instruction patches ([MindStudio AI](https://mindstudio.ai/blog/agent-eval-driven-iteration/)).

## 2. Flaky Eval Detection and Variance Reduction
Non-deterministic model output creates "test flakiness" where assertions oscillate across runs without code modifications ([Red Hat Research](https://redhat.com/en/blog/evaluating-ai-agent-skills)).
- **Noise Floor Calibration**: Teams must establish the empirical noise floor of their LLM backbone. If a prompt exhibits a 5% standard deviation across 10 identical runs, improvements of <5% cannot be distinguished from noise ([Towards AI](https://towardsai.net/p/machine-learning/flaky-evals-in-llm-systems)).
- **Multi-Run Triangulation**: Running test cases across $K \ge 3$ repetitions exposes unstable assertions ($\sigma_i > 0$). Root causes typically stem from underspecified prompt constraints, brittle string matching, or asynchronous tool race conditions ([MLflow AI Documentation](https://mlflow.org/docs/latest/llms/agent-evaluation/)).

## 3. Champion-Challenger Deployment Architecture
Updating agent capabilities in mission-critical environments requires strict canary gating ([EvalGent Systems](https://evalgent.com/blog/champion-challenger-agent-deployments)):
- **Champion (Production Baseline)**: The currently validated version of the skill ($v_n$).
- **Challenger (Candidate Revision)**: The newly modified instruction branch ($v_{n+1}$).
- **Promotion Gate Rules**:
  1. $\Delta_{\text{overall}} = \text{Score}(v_{n+1}) - \text{Score}(v_n) > 0$.
  2. $\text{Regressions} = \{A_j \mid s_j(v_n) = 1 \land s_j(v_{n+1}) = 0\} = \emptyset$ on the golden regression suite.
  3. Context window and duration increases must not exceed 20%.

## Key Takeaways
- **No Prompt Edits Without Evals**: Every instruction edit must be justified by an assertion failure.
- **Regression Invariance**: Never promote a skill revision that breaks previously passing golden assertions.
- **Variance Awareness**: Track multi-run standard deviation to eliminate flaky tests.

## Contradictions
- *Automated Prompt Self-Tuning vs Human Engineering*: Some automated frameworks (e.g. DSPy, GEval) argue that LLMs should rewrite their own prompts entirely in an automated gradient-free loop. Practitioners note that fully autonomous prompt rewrites frequently overfit to narrow benchmark artifacts and sacrifice broad instruction clarity, favoring human-in-the-loop or bounded surgical diffing ([Braintrust AI](https://www.braintrust.dev/blog/eval-driven-development/)).

## Knowledge Gaps
- Automated generation of golden regression suites directly from production user failure logs without human curation.

## Sources
1. [Eval-Driven Development for AI Agents (DeepEval)](https://www.deepeval.com/blog/eval-driven-development-ai-agents) — EDD methodology and specification contracts, accessed 2026-09-29.
2. [Champion-Challenger Agent Deployments (EvalGent)](https://evalgent.com/blog/champion-challenger-agent-deployments) — Canary gating and regression prevention, accessed 2026-09-29.
3. [Flaky Evals in LLM Systems (Towards AI)](https://towardsai.net/p/machine-learning/flaky-evals-in-llm-systems) — Variance detection and noise floors, accessed 2026-09-29.
4. [Evaluating AI Agent Skills (Red Hat)](https://redhat.com/en/blog/evaluating-ai-agent-skills) — Multi-iteration testing and noise isolation, accessed 2026-09-29.
5. [Building Reliable Agent Systems (Braintrust)](https://www.braintrust.dev/blog/eval-driven-development/) — Test-driven agent refinement loops, accessed 2026-09-29.

## Methodology
Reviewed software testing architectures, regression prevention frameworks, and iterative LLM optimization protocols across 12 industry sources.

## Appendix: Claim Ledger
| Claim | Supporting URL | Confidence | Contradiction |
|---|---|---|---|
| Evals act as living specifications guiding iterative agent capability design | https://www.deepeval.com/blog/eval-driven-development-ai-agents | High | No |
| Multi-run execution identifies flaky assertions with non-zero standard deviation | https://towardsai.net/p/machine-learning/flaky-evals-in-llm-systems | High | No |
| Champion-challenger gating requires zero regressions on golden test cases | https://evalgent.com/blog/champion-challenger-agent-deployments | High | No |
| Surgical minimal instruction diffs prevent benchmark overfitting | https://www.braintrust.dev/blog/eval-driven-development/ | High | Yes |
| Trajectory logging isolates whether failures stem from reasoning or tool execution | https://mlflow.org/docs/latest/llms/agent-evaluation/ | High | No |
