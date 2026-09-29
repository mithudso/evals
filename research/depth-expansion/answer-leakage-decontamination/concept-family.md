# Concept Family Map: Answer Leakage Decontamination

## 1. Five-Neighborhood Family Taxonomy

```
                   [Parent Domain]
         Information Security & Benchmark Integrity
                        │
       ┌────────────────┼────────────────┐
       ▼                ▼                ▼
  [Siblings]        [Children]      [Adjacent]
- PII Scrubbing   - N-Gram Scan   - Prompt Injection
- Secret Redaction- Canary Probing- Data Sanitization
- Memo Audit      - Counterfactual- Train-Test Bleed
- Model Extraction- User Transform- Membership Infer.
                        │
                        ▼
                   [Frontier]
         - Semantic Embedding Decontamination
         - Automated Adversarial De-Leakage Agents
         - Zero-Knowledge Benchmark Verification
```

### Neighborhood Definitions
- **Parent / Super-domain**: Information Security & Benchmark Integrity (protocols ensuring test data remains isolated from evaluated systems).
- **Siblings**: PII Scrubbing, Secret/Credential Redaction, Model Extraction Defense, Memorization Auditing.
- **Children / Sub-concepts**: N-Gram Overlap Scanning, Canary Token Probing, Counterfactual Prompt Reformulation, Natural User Persona Transform.
- **Adjacent / Cross-over**: Prompt Injection Defense, Data Sanitization Pipelines, Train-Test Set Contamination, Membership Inference.
- **Frontier / Emerging**: Semantic Embedding Decontamination, Automated Adversarial De-Leakage Agents, Zero-Knowledge Benchmark Verification.

## 2. Competency Questions (CQ)
1. *How does answer leakage invalidate evaluation results?* -> Resolves to **The Anatomy of Answer Leakage**.
2. *What n-gram threshold identifies prompt contamination with skill instructions?* -> Resolves to **N-Gram Overlap Scanning**.
3. *How does counterfactual reformulation expose benchmark memorization?* -> Resolves to **Counterfactual Prompt Reformulation**.
4. *What transformation converts a prescriptive prompt into an authentic user request?* -> Resolves to **Natural User Persona Transform**.
5. *Why are canary tokens useful in tracking private documentation leaks?* -> Resolves to **Canary Token Probing**.

## 3. Scored Gaps & Prescriptive Analytics (CVS Table)

| Concept | Rel | Use | Nov | Int | Via | CVS | Decision | Rationale |
|---|---|---|---|---|---|---|---|---|
| **N-Gram Overlap Decontamination (Pass F)** | 5.0 | 5.0 | 4.0 | 4.5 | 5.0 | **4.70** | RESEARCH | Automated scanner for rule copying |
| **Counterfactual Prompt Perturbation** | 4.5 | 5.0 | 4.5 | 4.5 | 4.5 | **4.60** | RESEARCH | Verifies generalization vs memorization |
| **Natural User Persona Transform** | 5.0 | 4.5 | 3.5 | 4.0 | 5.0 | **4.45** | RESEARCH | Rewriting prompt from end-user perspective |
| **Canary Token Leak Probing** | 4.0 | 4.0 | 4.5 | 4.0 | 4.5 | **4.20** | RESEARCH | Detects private metadata leakage |
| **Zero-Knowledge Benchmark Verification** | 3.0 | 2.5 | 5.0 | 4.5 | 2.0 | **3.05** | SKIP | Cryptographic overhead unnecessary for prompt evals |

## 4. Saturation Verdict
- **Verdict**: `SATURATED-COVERAGE` (20 candidate concepts mapped across 5 neighborhoods).
- **CQ Resolution**: 100% of Competency Questions resolved.
