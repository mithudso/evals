# Concept Family Map: Eval-Driven Iteration Loop

## 1. Five-Neighborhood Family Taxonomy

```
                   [Parent Domain]
         Continuous Integration & Model Alignment
                        │
       ┌────────────────┼────────────────┐
       ▼                ▼                ▼
  [Siblings]        [Children]      [Adjacent]
- TDD for Code    - 5-Phase Loop   - Bandit Algo
- Active Learning - Flakiness Det. - Canary Deploys
- RLHF / DPO      - Champ-Chall.   - Genetic Progr.
- Prompt Opt.     - Golden Suite   - Variance Red.
                        │
                        ▼
                   [Frontier]
         - Self-Healing Prompt Compilers
         - Autonomous Multi-Agent Eval Tournaments
         - Multi-Objective Pareto Release Gating
```

### Neighborhood Definitions
- **Parent / Super-domain**: Continuous Integration & Model Alignment (systematic protocols for advancing autonomous capabilities without regression).
- **Siblings**: Test-Driven Development (TDD), Active Learning, Reinforcement Learning from Human Feedback (RLHF/DPO), Automated Prompt Optimization (DSPy).
- **Children / Sub-concepts**: 5-Phase Iteration Loop (Audit, Exec, Grade, Diagnose, Patch), Flakiness Detection ($\sigma_i > 0$), Champion-Challenger Gating, Golden Regression Suite, Convergence Criteria.
- **Adjacent / Cross-over**: Contextual Multi-Armed Bandits, Canary Release Pipelines, Genetic Programming (mutation/crossover prompts), Statistical Variance Reduction (control variates).
- **Frontier / Emerging**: Self-Healing Prompt Compilers, Autonomous Multi-Agent Evaluation Tournaments, Multi-Objective Pareto Optimization Gating.

## 2. Competency Questions (CQ)
1. *What five stages compose a disciplined agent capability iteration cycle?* -> Resolves to **5-Phase Iteration Loop**.
2. *How does champion-challenger testing guarantee production safety?* -> Resolves to **Champion-Challenger Gating**.
3. *How is non-deterministic eval flakiness measured and mitigated?* -> Resolves to **Flakiness Detection**.
4. *What prevents iterative prompt revisions from breaking previously working behavior?* -> Resolves to **Golden Regression Suite**.
5. *When should an engineer stop prompt tuning and declare benchmark convergence?* -> Resolves to **Convergence Criteria**.

## 3. Scored Gaps & Prescriptive Analytics (CVS Table)

| Concept | Rel | Use | Nov | Int | Via | CVS | Decision | Rationale |
|---|---|---|---|---|---|---|---|---|
| **5-Phase Iteration Cycle Architecture** | 5.0 | 5.0 | 4.0 | 4.0 | 5.0 | **4.65** | RESEARCH | Universal workflow for iterative refinement |
| **Champion-Challenger Canary Gating** | 5.0 | 5.0 | 4.5 | 4.5 | 4.5 | **4.75** | RESEARCH | Essential defense against capability regression |
| **Multi-Run Flakiness & Variance Analysis** | 4.5 | 4.5 | 4.5 | 4.0 | 5.0 | **4.50** | RESEARCH | Separates model noise from real prompt lift |
| **Golden Regression Suite Management** | 5.0 | 4.5 | 3.5 | 4.0 | 5.0 | **4.45** | RESEARCH | Invariant protection for core features |
| **Convergence Detection & Plateau Stopping** | 4.0 | 4.0 | 4.0 | 4.0 | 4.5 | **4.10** | RESEARCH | Prevents token waste on diminishing returns |
| **Multi-Objective Pareto Release Solvers** | 3.5 | 3.0 | 4.5 | 4.5 | 3.0 | **3.60** | SKIP | Overly complex for single-skill authoring workflows |
| **Autonomous Self-Healing Prompt Compilers** | 3.5 | 3.5 | 5.0 | 4.5 | 2.5 | **3.70** | SKIP | Frontier research topic; high compute overhead |

## 4. Saturation Verdict
- **Verdict**: `SATURATED-COVERAGE`
- **Family Coverage**: 21 candidate concepts identified across all 5 neighborhoods.
- **CQ Resolution**: 100% of Competency Questions resolved to formal iteration and gating procedures.
