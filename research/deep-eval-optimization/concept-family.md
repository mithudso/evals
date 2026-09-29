# Concept Family Map: Deep Eval Optimization

## 1. Five-Neighborhood Family Taxonomy

```
                   [Parent Domain]
             Meta-Evaluation & Quality Assurance
                        │
       ┌────────────────┼────────────────┐
       ▼                ▼                ▼
  [Siblings]        [Children]      [Adjacent]
- Static Analysis - 12 Passes (A-L)- Benchmark Auditing
- Mutation Testing- Leakage Guard  - Data Contamination
- Red-Teaming     - Discrim. Power - Test Flakiness
- Fuzzing Evals   - Schema Valid   - Reward Hacking
                        │
                        ▼
                   [Frontier]
         - Self-Auditing Synthetic Evals
         - Automated Benchmark Decontamination
         - Adversarial Eval-Hacking Agents
```

### Neighborhood Definitions
- **Parent / Super-domain**: Meta-Evaluation & Quality Assurance (evaluating, validating, and certifying evaluation systems).
- **Siblings**: Static Analysis of Test Code, Mutation Testing of Test Suites, Red-Teaming of Judges, Eval Fuzzing.
- **Children / Sub-concepts**: The 12 Analytical Passes (A through L), Answer Leakage Prevention, Discriminative Power Analysis, Prompt Realism (Ecological Validity), Schema Compliance.
- **Adjacent / Cross-over**: Benchmark Auditing, Dataset Contamination Scanners, Test Flakiness Analytics, Reward Hacking Mitigation.
- **Frontier / Emerging**: Self-Auditing Synthetic Evals, Automated Benchmark Decontamination, Adversarial Eval-Hacking Agents.

## 2. Competency Questions (CQ)
1. *What 12 analytical dimensions constitute a complete audit of an agent evaluation suite?* -> Resolves to **The 12 Analytical Passes (A–L)**.
2. *How is answer leakage detected and purged from evaluation prompts?* -> Resolves to **Answer Leakage Prevention (Pass F)**.
3. *How does discriminative power analysis prevent evaluation illusion?* -> Resolves to **Discriminative Power Analysis (Pass B)**.
4. *Why must synthetic eval prompts be rewritten with authentic user noise?* -> Resolves to **Prompt Realism & Ecological Validity (Pass A)**.
5. *What schema validation ensures eval suites parse cleanly across automated runners?* -> Resolves to **Schema Compliance (Pass L)**.

## 3. Scored Gaps & Prescriptive Analytics (CVS Table)

| Concept | Rel | Use | Nov | Int | Via | CVS | Decision | Rationale |
|---|---|---|---|---|---|---|---|---|
| **12-Pass Analytical Framework (Passes A–L)** | 5.0 | 5.0 | 4.5 | 4.5 | 5.0 | **4.80** | RESEARCH | Core architectural standard for eval auditing |
| **Answer Leakage & Contamination Auditing** | 5.0 | 5.0 | 4.5 | 4.0 | 4.5 | **4.65** | RESEARCH | Eliminates prompt hints that invalidate tests |
| **Discriminative Power & Baseline Delta Analysis** | 5.0 | 5.0 | 4.0 | 4.0 | 4.5 | **4.60** | RESEARCH | Guarantees benchmarks separate skill from base |
| **Prompt Realism & Ecological Noise Injection** | 4.5 | 4.5 | 4.0 | 4.5 | 5.0 | **4.45** | RESEARCH | Bridges gap between synthetic tests and users |
| **Eval Fixture Minification & Context Budgeting** | 4.0 | 4.5 | 3.5 | 4.0 | 5.0 | **4.20** | RESEARCH | Prevents token exhaustion during eval batches |
| **Adversarial Benchmark-Hacking Agents** | 3.5 | 3.0 | 5.0 | 4.5 | 2.5 | **3.65** | SKIP | Frontier research topic; requires complex red-team setup |
| **Automated Data Contamination Scanners** | 3.5 | 3.5 | 4.0 | 4.0 | 3.0 | **3.60** | SKIP | Primarily for LLM pre-training; less critical for skills |

## 4. Saturation Verdict
- **Verdict**: `SATURATED-COVERAGE`
- **Family Exhaustion**: 22 candidate concepts identified across all 5 neighborhoods.
- **Competency Resolution**: 100% of Competency Questions resolved to formal DEO passes and audit procedures.
