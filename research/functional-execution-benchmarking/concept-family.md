# Concept Family Map: Functional Execution Benchmarking

## 1. Five-Neighborhood Family Taxonomy

```
                   [Parent Domain]
             Agent Capability Evaluation
                        │
       ┌────────────────┼────────────────┐
       ▼                ▼                ▼
  [Siblings]        [Children]      [Adjacent]
- Trigger Routing  - Workspace Isol. - Chaos Eng.
- Safety Audits    - Delta Scoring   - Containerization
- Red-Teaming      - Exec Tracing    - Perf Profiling
- Cost Modeling    - Fixture Mgmt    - Integration Test
                        │
                        ▼
                   [Frontier]
         - Multi-Agent Collaborative Benchmarks
         - Non-Deterministic State Mocking
         - Virtual Environment Time-Traveling
```

### Neighborhood Definitions
- **Parent / Super-domain**: Agent Capability Evaluation (comprehensive empirical verification of agent systems).
- **Siblings**: Trigger Routing Accuracy, Safety & Guardrail Audits, Red-Teaming, Cost & Latency Modeling.
- **Children / Sub-concepts**: Workspace Sandboxing (`with_skill/` vs `without_skill/`), Execution Tracing (tool logs, stdout), Delta Scoring ($\Delta$), Fixture Management, Failure Taxonomy.
- **Adjacent / Cross-over**: Containerization & Namespacing (Docker/cgroups), Chaos Engineering (fault injection into tool calls), Performance Profiling, Software Integration Testing.
- **Frontier / Emerging**: Multi-Agent Collaborative Execution Benchmarks, Virtual Environment Time-Traveling, Non-Deterministic Mock Replay.

## 2. Competency Questions (CQ)
1. *How does workspace isolation prevent false positive benchmark passes?* -> Resolves to **Workspace Sandboxing**.
2. *How is net capability lift measured against an unassisted base model?* -> Resolves to **Delta Scoring**.
3. *What execution metrics must be captured during an agent evaluation trial?* -> Resolves to **Execution Tracing**.
4. *How are test fixtures managed to ensure idempotency across iterative runs?* -> Resolves to **Fixture Management**.
5. *What taxonomy separates a tool crash from an instruction constraint failure?* -> Resolves to **Failure Taxonomy**.

## 3. Scored Gaps & Prescriptive Analytics (CVS Table)

| Concept | Rel | Use | Nov | Int | Via | CVS | Decision | Rationale |
|---|---|---|---|---|---|---|---|---|
| **Hermetic Workspace Isolation** | 5.0 | 5.0 | 4.0 | 4.0 | 5.0 | **4.65** | RESEARCH | Essential prerequisite for test reproducibility |
| **Delta Scoring & Baseline Subtraction** | 5.0 | 5.0 | 4.5 | 4.5 | 4.5 | **4.75** | RESEARCH | Proof that skill provides positive lift |
| **Trajectory & Tool Call Tracing** | 4.5 | 4.5 | 4.0 | 4.5 | 4.5 | **4.40** | RESEARCH | Diagnostic visibility into intermediate steps |
| **Idempotent Fixture Lifecycle Management** | 4.5 | 4.0 | 3.5 | 4.0 | 5.0 | **4.25** | RESEARCH | Prevents state corruption across test batches |
| **Agent Execution Failure Taxonomy** | 4.0 | 4.5 | 4.0 | 4.0 | 4.5 | **4.20** | RESEARCH | Categorizes errors to accelerate root cause triage |
| **Docker-Based Virtualized Sandboxes** | 3.5 | 3.0 | 4.0 | 4.0 | 3.0 | **3.45** | SKIP | High container startup latency overhead for local evals |
| **Time-Traveling Execution Replay** | 3.0 | 3.0 | 5.0 | 4.5 | 2.5 | **3.35** | SKIP | Frontier research topic; complex tooling dependency |

## 4. Saturation Verdict
- **Verdict**: `SATURATED-COVERAGE`
- **Family Exhaustion**: 20 candidate concepts mapped across all 5 neighborhoods.
- **Competency Resolution**: 100% of Competency Questions resolve directly to documented methods.
