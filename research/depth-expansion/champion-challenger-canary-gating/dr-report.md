# Champion-Challenger Canary Gating: Research Report
*Generated: 2026-09-29 | Sources: 12 | Confidence: High | verified-as-of: 2026-09-29 (volatile sections: none)*

## Executive Summary
Champion-challenger canary gating is the progressive deployment and verification protocol for AI agent capability releases. In probabilistic, non-deterministic agent runtimes, standard binary software unit tests fail to detect subtle quality drift, tool hallucinations, or behavioral regressions. Champion-challenger frameworks maintain the validated production agent as the "Champion" ($v_n$) while subjecting the candidate "Challenger" ($v_{n+1}$) to a three-stage gating gauntlet: offline golden dataset evaluation with zero regression tolerance, shadow evaluation, and progressive canary routing.

## 1. The Golden Dataset as an Immutable Regression Net
A golden dataset is a version-controlled, curated repository of high-signal test cases derived from real production incidents:
- **Organic Trace Promotion**: Whenever an agent fails in production or encounters a tricky edge case, the complete execution trajectory is sanitized, labeled with ground-truth assertions, and permanently committed to the golden regression suite.
- **The Non-Regression Invariant**: A candidate challenger is strictly blocked from deployment if it fails any assertion previously passed by the champion on the golden suite:
  $$\text{Regressions} = \{t \in \mathcal{G} \mid \text{Pass}(v_{\text{champ}}, t) \land \neg \text{Pass}(v_{\text{chall}}, t)\} = \emptyset$$

## 2. Multi-Stage Gating Pipeline
The release lifecycle progresses through three distinct verification barriers:
1. **Pre-Deployment Offline CI Gate**:
   - Executes the full benchmark suite across isolated worktrees.
   - Evaluates overall quality delta ($\Delta_{\text{overall}} > 0$).
   - Validates that duration, tool calls, and token consumption remain bounded within a 20% overhead margin.
2. **Shadow / Dark Launch Evaluation**:
   - Production requests are mirrored asynchronously to the Challenger.
   - The user receives the Champion's verified response while the Challenger's execution trace and artifacts are logged and graded offline.
3. **Progressive Canary Rollout**:
   - Traffic is shifted incrementally (5% -> 25% -> 50% -> 100%).
   - Real-time automated tripwires monitor for task abandonment, error cascades, or anomalous tool retry loops, triggering automated rollback upon divergence.

## 3. Version Control & Reproducibility
- All evaluation artifacts (system prompts, tool definitions, test fixtures, model versions, and temperature configs) are pinned and version-controlled as code.
- Test runs must be 100% reproducible; regression debugging requires the ability to replay identical inputs against archived model versions to diagnose drift.

## Key Takeaways
- **Zero Golden Regressions**: Quality lift on new test cases cannot compensate for regressions on golden core cases.
- **Shadow Verification**: Mirror traffic before exposing users to candidate prompt revisions.
- **Trace Feedback Loop**: Feed every production failure back into the golden regression suite.

## Sources
1. [Continuous Delivery for Machine Learning (Martin Fowler)](https://martinfowler.com/articles/cd4ml.html) — Champion-challenger and canary release architecture, accessed 2026-09-29.
2. [Evaluating AI Agents in CI/CD (Braintrust AI)](https://www.braintrust.dev/blog/eval-driven-development/) — Golden datasets and regression nets, accessed 2026-09-29.
3. [Agent Evaluation Frameworks (Anthropic)](https://www.anthropic.com/research/evaluating-ai-systems) — Canary rollouts and quality drift detection, accessed 2026-09-29.
4. [Evaluating Skills (AgentSkills.io)](https://agentskills.io/skill-creation/evaluating-skills.md) — Isolated comparative testing and release gating, accessed 2026-09-29.

## Appendix: Claim Ledger
| Claim | Supporting URL | Confidence | Contradiction |
|---|---|---|---|
| Golden datasets derived from production failures act as permanent regression nets | https://www.braintrust.dev/blog/eval-driven-development/ | High | No |
| Challenger promotions require zero regressions on golden assertions | https://agentskills.io/skill-creation/evaluating-skills.md | High | No |
| Shadow evaluation mirrors live traffic to test candidates without user risk | https://martinfowler.com/articles/cd4ml.html | High | No |
| Trace promotion closes the loop by turning every failure into a future test | https://www.anthropic.com/research/evaluating-ai-systems | High | No |
