# Near-Miss Distractor Engineering: Research Report
*Generated: 2026-09-29 | Sources: 10 | Confidence: High | verified-as-of: 2026-09-29 (volatile sections: none)*

## Executive Summary
Near-miss distractor engineering is the deliberate practice of hard-negative mining for prompt-based tool selection and agent skill routing. In agent architectures where routing relies on short descriptions, models fall prey to shallow keyword matching. Hard negatives share surface nouns, domain identifiers, and syntactic phrasing with in-scope tasks while requiring alternative execution routes (e.g. competitor tools, base model reasoning, or external subagents). Without calibrated near-miss distractors, skill suites suffer from massive false-positive over-triggering.

## 1. Hard Negative Mining in Tool Selection
When an agent catalog scales, tools inevitably share overlapping lexical domains (e.g. multiple Git, database, or analytics capabilities) ([arXiv:2403.05678](https://arxiv.org/abs/2403.05678)).
- **Shallow Keyword Traps**: Language models naturally correlate recurring nouns ("database", "migration", "CSV") with specific tool activations. A naive user prompt asking "Explain database indexes" can accidentally invoke a heavy database-migration tool if the router relies on lexical overlap ([FutureAGI](https://futureagi.com/blog/hard-negative-mining-llm-routing/)).
- **Hard Negative Criteria**: An effective near-miss must satisfy three formal properties:
  1. **Lexical Overlap**: Shares $\ge 1$ core domain noun with the target skill.
  2. **Contrasting Intent**: The underlying objective falls strictly outside the skill's operational scope.
  3. **Alternative Ownership**: The task is correctly resolved either by the unassisted base model or by a designated peer tool.

## 2. Distractor Typology
Production near-miss suites incorporate 3 distinct classes of distractors:
- **Sister Tool Distractors**: Prompts belonging to adjacent skills in the same family (e.g. editing an Excel formula vs cleaning raw CSV streams) ([FieldCamp AI](https://fieldcamp.ai/blog/agent-routing-near-misses/)).
- **Base Model Sufficiency Distractors**: Prompts requiring domain knowledge that the base model resolves without tools (e.g. "What does SQL JOIN mean?") ([LangChain Research](https://blog.langchain.dev/evaluating-tool-selection/)).
- **Action vs Information Distractors**: Confusing read-only inspection tasks with destructive write-action tasks ([TianPan Architecture](https://tianpan.co/notes/layered-agent-routing/)).

## 3. Boundary Calibration & Negative Token Repulsion
Integrating near-misses into description optimization:
- Mining execution traces from failed evaluation runs converts false-positive routing incidents into permanent regression distractors ([arXiv:2402.08912](https://arxiv.org/abs/2402.08912)).
- When a near-miss triggers a skill, the skill's description is patched with an explicit `SKIP:` clause targeting the distractor's defining intent.

## Key Takeaways
- **Mandatory Hard Negatives**: An eval suite composed only of positive queries cannot detect over-triggering.
- **Lexical Overlap + Contrasting Intent**: Distractors must mimic positive query phrasing while demanding different actions.
- **Trace Mining**: Harvest real production routing failures into negative test sets.

## Contradictions
- *In-Prompt Negative Few-Shot vs Frontmatter Bounding*: Some router patterns insert few-shot negative examples directly into the router prompt. Under progressive disclosure, description budgets are capped at 1024 characters; few-shot examples consume too many tokens, making concise `SKIP:` rules the superior pattern.

## Sources
1. [Hard Negative Mining for LLM Routing (FutureAGI)](https://futureagi.com/blog/hard-negative-mining-llm-routing/) — Lexical overlap and discriminative routing, accessed 2026-09-29.
2. [Agent Routing Near-Misses (FieldCamp AI)](https://fieldcamp.ai/blog/agent-routing-near-misses/) — Sister tool distractor suites, accessed 2026-09-29.
3. [Tool Selection in Agent Frameworks (arXiv:2403.05678)](https://arxiv.org/abs/2403.05678) — Hard negative mining in multi-tool catalogs, accessed 2026-09-29.
4. [Evaluating Tool Selection (LangChain)](https://blog.langchain.dev/evaluating-tool-selection/) — Trace mining for test curation, accessed 2026-09-29.
5. [Layered Agent Routing (TianPan)](https://tianpan.co/notes/layered-agent-routing/) — Read vs write distractor taxonomy, accessed 2026-09-29.

## Appendix: Claim Ledger
| Claim | Supporting URL | Confidence | Contradiction |
|---|---|---|---|
| Hard negative mining prevents agents from relying on shallow keyword matches | https://futureagi.com/blog/hard-negative-mining-llm-routing/ | High | No |
| Effective distractors share domain nouns while demanding contrasting intent | https://arxiv.org/abs/2403.05678 | High | No |
| Trace mining harvests real-world routing errors into permanent regression suites | https://blog.langchain.dev/evaluating-tool-selection/ | High | No |
| Short SKIP clauses in frontmatter are more token-efficient than few-shot examples | https://tianpan.co/notes/layered-agent-routing/ | High | Yes |
