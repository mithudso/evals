# Concept Family Map: Negative Boundary Tripwires

## 1. Five-Neighborhood Family Taxonomy

```
                   [Parent Domain]
             Software Safety & Fault Tolerance
                        │
       ┌────────────────┼────────────────┐
       ▼                ▼                ▼
  [Siblings]        [Children]      [Adjacent]
- Guardrails       - Hallucination - Circuit Breakers
- Canary Tokens    - Pollution     - Honeypots
- Fuzz Invariants  - AI-isms       - Static Taint Anal.
- Rate Limiters    - Placeholders  - Zero-Trust Arch.
                        │
                        ▼
                   [Frontier]
         - Dynamic Semantic Tripwires
         - Autonomous Red-Team Probe Injection
         - Differential Trajectory Tripwires
```

### Neighborhood Definitions
- **Parent / Super-domain**: Software Safety & Fault Tolerance (mechanisms that prevent catastrophic failures by halting operations upon boundary breach).
- **Siblings**: Output Guardrails (Llama Guard), Canary Tokens, Fuzzing Invariant Checkers, API Rate Limiters.
- **Children / Sub-concepts**: Hallucination Tripwires, Filesystem Pollution Tripwires, Conversational AI-ism Tripwires, Placeholder Detection Tripwires.
- **Adjacent / Cross-over**: Electrical Circuit Breakers, Cyber Security Honeypots, Static Taint Analysis, Zero-Trust Architecture.
- **Frontier / Emerging**: Dynamic Semantic Tripwires, Autonomous Red-Team Probe Injection, Differential Trajectory Tripwires.

## 2. Competency Questions (CQ)
1. *Why does a single negative tripwire violation zero out a test score?* -> Resolves to **Circuit Breaker Multipliers**.
2. *How do honeypot canary files detect agent privilege escalation?* -> Resolves to **Honeypot Testing**.
3. *What regex checks eliminate conversational filler and AI-isms from technical outputs?* -> Resolves to **Conversational AI-ism Tripwires**.
4. *How is filesystem pollution detected programmatically after an agent run?* -> Resolves to **Filesystem Pollution Tripwires**.
5. *Why are negative bounds essential when evaluating generative code agents?* -> Resolves to **Hallucination Tripwires**.

## 3. Scored Gaps & Prescriptive Analytics (CVS Table)

| Concept | Rel | Use | Nov | Int | Via | CVS | Decision | Rationale |
|---|---|---|---|---|---|---|---|---|
| **Multiplicative Circuit Breaker Math** | 5.0 | 5.0 | 4.0 | 4.5 | 5.0 | **4.70** | RESEARCH | Gating logic for zero-tolerance safety |
| **Filesystem Pollution & Leak Tripwires** | 4.5 | 5.0 | 4.5 | 4.0 | 5.0 | **4.60** | RESEARCH | Prevents workspace corruption |
| **Canary Honeypot Files in Sandboxes** | 4.0 | 4.5 | 4.5 | 4.5 | 4.5 | **4.40** | RESEARCH | Active tripwire defense against overreach |
| **Dynamic Semantic Taint Solvers** | 3.5 | 3.0 | 5.0 | 4.5 | 2.5 | **3.55** | SKIP | Requires formal proof assistant infrastructure |

## 4. Saturation Verdict
- **Verdict**: `SATURATED-COVERAGE` (20 candidate concepts mapped across 5 neighborhoods).
- **CQ Resolution**: 100% of Competency Questions resolved.
