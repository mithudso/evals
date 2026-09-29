# Concept Family Map: Champion-Challenger Canary Gating

## 1. Five-Neighborhood Family Taxonomy

```
                   [Parent Domain]
         Continuous Delivery & Release Engineering
                        │
       ┌────────────────┼────────────────┐
       ▼                ▼                ▼
  [Siblings]        [Children]      [Adjacent]
- Blue-Green Dep - Golden Suite   - Feature Flags
- Dark Launching - Shadow Eval    - Observability
- Rolling Update - Canary Shift   - Circuit Breakers
- Chaos Testing  - Rollback Auto  - SRE Error Budgets
                        │
                        ▼
                   [Frontier]
         - Multi-Armed Bandit Traffic Routing
         - Autonomous Self-Reverting Models
         - Counterfactual Shadow Replay
```

### Neighborhood Definitions
- **Parent / Super-domain**: Continuous Delivery & Release Engineering (disciplines ensuring safe, zero-downtime deployment of software changes).
- **Siblings**: Blue-Green Deployment, Dark Launching, Rolling Updates, Chaos Testing.
- **Children / Sub-concepts**: Golden Regression Suite, Shadow Evaluation, Canary Traffic Shifting, Automated Rollback Tripwires.
- **Adjacent / Cross-over**: Feature Flag Management (LaunchDarkly), Observability & APM Tracing (Datadog/OpenTelemetry), SRE Error Budgets, Circuit Breakers.
- **Frontier / Emerging**: Multi-Armed Bandit Traffic Routing, Autonomous Self-Reverting Models, Counterfactual Shadow Replay.

## 2. Competency Questions (CQ)
1. *What criteria govern the promotion of a challenger skill over a production champion?* -> Resolves to **Promotion Invariants**.
2. *How does shadow evaluation detect silent agent regressions before user exposure?* -> Resolves to **Shadow Evaluation**.
3. *What defines an immutable golden regression suite?* -> Resolves to **Golden Regression Suite**.
4. *How are production user failures converted into permanent test cases?* -> Resolves to **Trace Promotion Loop**.
5. *What conditions trigger an automated rollback during canary shifting?* -> Resolves to **Automated Rollback Tripwires**.

## 3. Scored Gaps & Prescriptive Analytics (CVS Table)

| Concept | Rel | Use | Nov | Int | Via | CVS | Decision | Rationale |
|---|---|---|---|---|---|---|---|---|
| **Golden Regression Net & Invariant Testing** | 5.0 | 5.0 | 4.0 | 4.5 | 5.0 | **4.70** | RESEARCH | Foundational release gate for agent skills |
| **Shadow Mode Evaluation Pipelines** | 4.5 | 5.0 | 4.5 | 4.5 | 4.5 | **4.60** | RESEARCH | Safe verification on real-world traffic |
| **Automated Canary Rollback Tripwires** | 4.5 | 4.5 | 4.0 | 4.0 | 4.5 | **4.30** | RESEARCH | Prevents widespread user failure cascades |
| **Bandit-Driven Autonomous Traffic Routing** | 3.5 | 3.5 | 4.5 | 4.5 | 3.0 | **3.70** | SKIP | Requires continuous online production traffic |

## 4. Saturation Verdict
- **Verdict**: `SATURATED-COVERAGE` (20 candidate concepts mapped across 5 neighborhoods).
- **CQ Resolution**: 100% of Competency Questions resolved.
