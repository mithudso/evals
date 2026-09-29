# Concept Family Map: Near-Miss Distractor Engineering

## 1. Five-Neighborhood Family Taxonomy

```
                   [Parent Domain]
             Negative Sampling & Contrastive Learning
                        │
       ┌────────────────┼────────────────┐
       ▼                ▼                ▼
  [Siblings]        [Children]      [Adjacent]
- Random Negatives - Sister-Tool   - Contrastive Loss
- Hard Mining      - Base-Model    - Triplet Loss
- Adversarial Pert - Action/Read   - Word2Vec Negatives
- InfoNCE Bounds   - Trace Mining  - Boundary Margin
                        │
                        ▼
                   [Frontier]
         - Synthetic Distractor Synthesis
         - Dynamic Negative Shuffling
         - Cross-Model Transfer Distractors
```

### Neighborhood Definitions
- **Parent / Super-domain**: Negative Sampling & Contrastive Learning (training/evaluating systems using negative instances to sharpen decision boundaries).
- **Siblings**: Random Negative Sampling, In-Batch Hard Negative Mining, Adversarial Token Perturbations, InfoNCE Gating.
- **Children / Sub-concepts**: Sister-Tool Distractors, Base-Model Sufficiency Distractors, Action/Information Distractors, Trace-Mined Regression Distractors.
- **Adjacent / Cross-over**: Contrastive Loss (InfoNCE), Triplet Margin Loss, Support Vector Machine (SVM) Boundary Margins, Out-of-Distribution Rejection.
- **Frontier / Emerging**: Autonomous Synthetic Distractor Generation, Dynamic Negative Shuffling, Cross-Model Transfer Distractor Benchmarking.

## 2. Competency Questions (CQ)
1. *How does hard-negative mining differ from random negative sampling in tool evals?* -> Resolves to **Hard Negative Mining vs Random Negatives**.
2. *What criteria define a valid sister-tool distractor?* -> Resolves to **Sister-Tool Distractors**.
3. *How are production false-positive routing incidents converted into permanent test cases?* -> Resolves to **Trace-Mined Regression Distractors**.
4. *What prevents a router from confusing read-only analysis with destructive operations?* -> Resolves to **Action/Information Distractors**.
5. *Why are near-miss distractors required to achieve <=10% false-positive thresholds?* -> Resolves to **Boundary Margin Calibration**.

## 3. Scored Gaps & Prescriptive Analytics (CVS Table)

| Concept | Rel | Use | Nov | Int | Via | CVS | Decision | Rationale |
|---|---|---|---|---|---|---|---|---|
| **Sister-Tool Distractor Taxonomy** | 5.0 | 5.0 | 4.0 | 4.5 | 5.0 | **4.70** | RESEARCH | Essential boundary test between adjacent skills |
| **Trace-Mined Hard Negative Pipelines** | 4.5 | 5.0 | 4.5 | 4.5 | 4.5 | **4.60** | RESEARCH | Direct conversion of failure logs to tests |
| **Action vs Information Distractor Patterns** | 4.5 | 4.5 | 4.0 | 4.0 | 5.0 | **4.40** | RESEARCH | Prevents destructive execution accidents |
| **Base Model Sufficiency Negative Controls** | 4.5 | 4.0 | 3.5 | 4.0 | 5.0 | **4.20** | RESEARCH | Protects against tool bloat for trivial tasks |
| **Synthetic LLM Distractor Generators** | 3.5 | 3.5 | 4.5 | 4.5 | 3.5 | **3.85** | SKIP | Risk of generating unrealistic or non-discriminating tests |

## 4. Saturation Verdict
- **Verdict**: `SATURATED-COVERAGE` (20 candidate concepts mapped across 5 neighborhoods).
- **CQ Resolution**: 100% of Competency Questions resolved.
