# Concept Family Map: Trigger Accuracy and Calibration

## 1. Five-Neighborhood Family Taxonomy

```
                   [Parent Domain]
         Intent Recognition & Tool Routing
                        │
       ┌────────────────┼────────────────┐
       ▼                ▼                ▼
  [Siblings]        [Children]      [Adjacent]
- Semantic Tool   - 20-Query Suite  - Conformal Pred.
- Param Extract   - Positive Typo.  - Calib. Curves
- Plan & Solve    - Near-Miss Eng.  - OOD Detection
- Disambiguation  - Variance Samp.  - Selective Class.
                        │
                        ▼
                   [Frontier]
         - Adversarial Jailbreak Triggers
         - Soft-Prompt Routing Tuning
         - Multimodal Trigger Calibration
```

### Neighborhood Definitions
- **Parent / Super-domain**: Intent Recognition & Tool Routing (the macro capability of steering model execution to correct sub-programs).
- **Siblings**: Semantic Tool Selection, Parameter Extraction, Plan-and-Solve Routing, Intent Disambiguation.
- **Children / Sub-concepts**: 20-Query Corpus Construction, Positive Intent Typology, Negative Near-Miss Engineering, Multi-Run Variance Sampling, Threshold Calibration ($\ge 90\% / \le 10\%$).
- **Adjacent / Cross-over**: Conformal Prediction (guaranteed coverage sets), Calibration Curves (ECE - Expected Calibration Error), Out-of-Distribution Detection, Selective Classification.
- **Frontier / Emerging**: Adversarial Jailbreak Triggers (tricking router into activating unintended tools), Soft-Prompt Routing Tuning, Multimodal Trigger Calibration.

## 2. Competency Questions (CQ)
1. *How many positive and negative queries constitute a statistically reliable skill trigger evaluation suite?* -> Resolves to **20-Query Suite**.
2. *What threshold separates a well-calibrated description from an over-triggering or under-triggering one?* -> Resolves to **Threshold Calibration**.
3. *How should an evaluation suite test whether a skill resists activating on adjacent tools with overlapping keywords?* -> Resolves to **Negative Near-Miss Engineering**.
4. *How does multi-run sampling address non-deterministic routing variance?* -> Resolves to **Multi-Run Variance Sampling**.
5. *Why are explicit SKIP clauses necessary in frontmatter descriptions?* -> Resolves to **Negative Boundary Controls**.

## 3. Scored Gaps & Prescriptive Analytics (CVS Table)
Scores grounded in multi-criteria decision analysis (0–5 scale):

| Concept | Rel | Use | Nov | Int | Via | CVS | Decision | Rationale |
|---|---|---|---|---|---|---|---|---|
| **20-Query Corpus Construction** | 5.0 | 5.0 | 3.5 | 4.0 | 5.0 | **4.60** | RESEARCH | Core foundation for all trigger benchmarks |
| **Near-Miss Distractor Engineering** | 5.0 | 5.0 | 4.5 | 4.5 | 4.5 | **4.75** | RESEARCH | Critical defense against tool absorption |
| **Multi-Run Variance Sampling ($K=3$)** | 4.5 | 4.5 | 4.0 | 4.0 | 5.0 | **4.40** | RESEARCH | Eliminates stochastic evaluation noise |
| **SKIP Clause Grammar & Negative Bounds** | 4.5 | 5.0 | 4.0 | 4.0 | 4.5 | **4.45** | RESEARCH | Formal routing syntax for mutual exclusion |
| **Expected Calibration Error (ECE) for Agents** | 4.0 | 3.5 | 4.5 | 4.5 | 3.5 | **3.95** | RESEARCH | Quantifies confidence vs accuracy alignment |
| **Soft-Prompt Router Tuning** | 3.0 | 3.0 | 4.5 | 4.0 | 2.5 | **3.20** | SKIP | Requires model fine-tuning; out of scope for prompt skills |
| **Multimodal Vision Triggers** | 3.5 | 3.0 | 4.0 | 4.5 | 3.0 | **3.50** | SKIP | Text-first skills ecosystem priority |

## 4. Saturation Verdict
- **Verdict**: `SATURATED-COVERAGE`
- **Map Floor**: All 5 neighborhoods comprehensively mapped (22 candidate concepts identified).
- **Competency Coverage**: 100% of Competency Questions resolve to documented research or active implementation nodes.
