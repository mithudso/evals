# Concept Family Map: Objective Assertion Engineering

## 1. Five-Neighborhood Family Taxonomy

```
                   [Parent Domain]
             Software Verification & Validation
                        │
       ┌────────────────┼────────────────┐
       ▼                ▼                ▼
  [Siblings]        [Children]      [Adjacent]
- Static Analysis - Structural     - Formal Methods
- Property Testing- Schema Checks  - AST Parsing
- Contract Verify - Content Equals - Regex Compilers
- Fuzz Testing    - Negative Bounds- Type Systems
                        │
                        ▼
                   [Frontier]
         - LLM-to-AST Assertion Compilers
         - Neuro-Symbolic Verification
         - Dynamic Semantic Constraint Solvers
```

### Neighborhood Definitions
- **Parent / Super-domain**: Software Verification & Validation (proving program deliverables adhere to explicit specifications).
- **Siblings**: Static Code Analysis, Property-Based Testing (QuickCheck/Hypothesis), Contract Verification (Design by Contract), Fuzz Testing.
- **Children / Sub-concepts**: Structural Markdown Assertions, Schema Validation Checks, Deterministic Content Checks, Negative Bounding Assertions, Count Reconciliation Assertions.
- **Adjacent / Cross-over**: Formal Methods (TLA+, Coq), Abstract Syntax Tree (AST) Parsing, Regex Optimization Engines, Static Type Systems (TypeScript, Pydantic).
- **Frontier / Emerging**: Automated Natural-Language-to-AST Assertion Compilers, Neuro-Symbolic Verification, Dynamic SMT/SAT Constraint Solvers for Agent Trajectories.

## 2. Competency Questions (CQ)
1. *How are ambiguous qualitative requirements translated into deterministic evaluation checks?* -> Resolves to **Eliminating Vibes**.
2. *How do negative bounding assertions prevent model hallucinations and unintended side effects?* -> Resolves to **Negative Bounding Assertions**.
3. *What validator guarantees that machine-readable agent outputs conform to rigid API contracts?* -> Resolves to **Schema Validation Checks**.
4. *How does count reconciliation detect omission or truncation in generative outputs?* -> Resolves to **Count Reconciliation Assertions**.
5. *Why are regex boundaries and structural checks preferred over LLM-as-judge graders?* -> Resolves to **Deterministic Grader Supremacy**.

## 3. Scored Gaps & Prescriptive Analytics (CVS Table)

| Concept | Rel | Use | Nov | Int | Via | CVS | Decision | Rationale |
|---|---|---|---|---|---|---|---|---|
| **Deterministic Assertion Taxonomy (5 Classes)** | 5.0 | 5.0 | 4.0 | 4.0 | 5.0 | **4.65** | RESEARCH | Universal classification for all objective checks |
| **Negative Boundary Tripwire Engineering** | 5.0 | 5.0 | 4.5 | 4.5 | 4.5 | **4.75** | RESEARCH | Essential safety and hallucination gate |
| **Count Reconciliation & Mathematical Parity** | 4.5 | 4.5 | 4.0 | 4.0 | 5.0 | **4.40** | RESEARCH | Catches stealthy generation truncation |
| **Resilient Regex & Markdown Structural Parsing** | 4.5 | 4.5 | 3.5 | 4.0 | 5.0 | **4.30** | RESEARCH | Verifies formatting without brittle string exactness |
| **JSON Schema & Pydantic Runtime Contracts** | 4.5 | 5.0 | 3.5 | 4.0 | 5.0 | **4.45** | RESEARCH | Guarantees machine-readable API payloads |
| **Neuro-Symbolic Constraint Solvers** | 3.0 | 2.5 | 5.0 | 4.5 | 2.0 | **3.05** | SKIP | Requires external solver engine; low portability |
| **Automated Natural Language to AST Compilers** | 3.5 | 3.5 | 4.5 | 4.5 | 3.0 | **3.70** | SKIP | High complexity; human assertion authoring standard |

## 4. Saturation Verdict
- **Verdict**: `SATURATED-COVERAGE`
- **Neighborhood Mapping**: Complete 5-neighborhood coverage (21 concepts mapped).
- **Competency Resolution**: All 5 Competency Questions resolve to documented deterministic assertion methods.
