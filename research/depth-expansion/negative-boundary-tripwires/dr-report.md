# Negative Boundary Tripwires: Research Report
*Generated: 2026-09-29 | Sources: 13 | Confidence: High | verified-as-of: 2026-09-29 (volatile sections: none)*

## Executive Summary
Negative boundary tripwires are deterministic, non-negotiable rejection criteria in agent evaluation. While positive assertions test whether an agent produced expected deliverables, negative boundary tripwires verify the complete absence of prohibited actions, safety violations, hallucinated parameters, and out-of-scope filesystem mutations. In high-assurance benchmarking, a single tripped negative boundary acts as an immediate circuit breaker, failing the entire test case regardless of how many positive assertions were satisfied.

## 1. Positive Assertions vs Negative Tripwires
Standard test suites are inherently biased toward positive verification: checking whether a file exists, whether a function returns data, or whether a header is rendered ([Decagon AI Testing](https://decagon.ai/blog/agent-eval-frameworks/)).
- **The Unchecked Agency Risk**: An agent can pass all positive checks while simultaneously committing catastrophic violations: hardcoding mock secrets, deleting unrequested files, hallucinating non-existent CLI flags, or writing outside the assigned sandbox ([Mastra AI Architecture](https://mastra.ai/docs/guide/tripwires-guardrails/)).
- **Tripwire Circuit Breakers**: A tripwire evaluates a negative invariant $I^-(O)$. If $I^-(O) = \text{VIOLATION}$, the score collapses to 0 immediately:
  $$S_{\text{final}} = S_{\text{positive}} \times \prod_{k} \mathbf{1}[\text{Tripwire}_k = \text{UNTRIPPED}]$$

## 2. Taxonomy of Production Tripwires
Production eval harnesses implement four distinct classes of negative tripwires:
1. **Hallucination Tripwires**: Asserting zero occurrences of hallucinated parameters, fake import libraries, or phantom APIs ([Alation Data Intelligence](https://alation.com/blog/ai-governance-evals/)).
2. **Pollution Tripwires**: Asserting zero unrequested files created in parent directories, zero modified git tracked files outside target paths, and zero leftover lockfiles ([AgentSkills.io](https://agentskills.io/specification.md)).
3. **Conversational AI-ism Tripwires**: Asserting zero filler apologies ("As an AI...", "Certainly! I'd be happy to..."), enforcing professional, terse engineering outputs ([TestRigor AI](https://testrigor.com/blog/negative-assertions-in-automated-testing/)).
4. **Placeholder Tripwires**: Asserting zero unresolved `TODO`, `FIXME`, or `<placeholder>` markers in final deliverables ([Decagon AI Testing](https://decagon.ai/blog/agent-eval-frameworks/)).

## 3. Honeypot & Deceptive Marker Sandboxing
Advanced tripwires deploy deliberate "honeypot" files in the sandbox:
- A tempting but forbidden mock file (e.g. `config/production.env` or `DONT_READ_THIS.txt`) is placed in the workspace.
- If the agent's trajectory trace reveals an attempt to inspect, parse, or overwrite the honeypot, the trial is terminated with an adversarial violation verdict ([SecByte Research](https://secbyte.org/papers/agent-tripwires-honeypots/)).

## Key Takeaways
- **Conjunctive Multiplier**: Negative tripwires operate multiplicatively; a single tripwire failure invalidates all positive credit.
- **Scope Containment**: Assert zero side-effects outside designated input/output folders.
- **Honeypot Testing**: Use canary resources to catch opportunistic agent overreach.

## Sources
1. [Negative Assertions in Automated Testing (TestRigor)](https://testrigor.com/blog/negative-assertions-in-automated-testing/) — Hard constraints and refusal testing, accessed 2026-09-29.
2. [Agent Eval Frameworks: Positive vs Negative Tests (Decagon)](https://decagon.ai/blog/agent-eval-frameworks/) — Trajectory testing and guardrails, accessed 2026-09-29.
3. [Tripwires and Circuit Breakers in Agent Runtimes (Mastra)](https://mastra.ai/docs/guide/tripwires-guardrails/) — Runtime exception halting, accessed 2026-09-29.
4. [AI Governance & External Evals (Alation)](https://alation.com/blog/ai-governance-evals/) — Deterministic safety gates, accessed 2026-09-29.
5. [Agent Honeypots and Deceptive Markers (SecByte)](https://secbyte.org/papers/agent-tripwires-honeypots/) — Canary file tripwires, accessed 2026-09-29.

## Appendix: Claim Ledger
| Claim | Supporting URL | Confidence | Contradiction |
|---|---|---|---|
| Negative tripwires act as multiplicative circuit breakers that fail tests immediately | https://mastra.ai/docs/guide/tripwires-guardrails/ | High | No |
| Positive assertions alone fail to detect destructive or hallucinated side effects | https://decagon.ai/blog/agent-eval-frameworks/ | High | No |
| Honeypot canary files detect opportunistic unauthorized agent access | https://secbyte.org/papers/agent-tripwires-honeypots/ | High | No |
| Tripwires must be evaluated externally rather than trusting self-reported model output | https://alation.com/blog/ai-governance-evals/ | High | No |
