# Rabbithole Dossier: Near-Miss Distractor Engineering

## 1. Scope & Boundary
- **IN SCOPE**: Semantic overlap metrics, lexical distractor generation, contrastive routing margins, prompt attention collision, sister-tool boundaries, trace-mining ingestion, false-positive containment.
- **OUT OF SCOPE**: Unsupervised pretraining negative caches, hardware vector memory indexing, image feature embeddings.

## 2. Pass 0: Baseline Atomic Claims
1. Near-miss distractors test an agent's ability to resist activating on out-of-scope tasks.
2. Distractors share keywords with target skills but require different tools or base models.
3. 10 negative queries are required per 20-query evaluation suite.
4. False positive rates must remain <= 10%.
5. Traces from production routing errors are harvested into new distractors.

## 3. Deepening Passes (Pass 1–4)

### Pass 1: Semantic Overlap vs Orthogonal Intent
- **The Lexical Vector Trap**: In transformer attention, high-IDF nouns (e.g. `kubernetes`, `terraform`, `postgresql`) generate strong attention peaks. If an agent has two skills sharing that noun (`k8s-pod-debugger` and `k8s-cluster-scaler`), the attention weight is split equally across both skills unless distinctive verb-object pairs (e.g. `debug pod crash` vs `adjust replica count`) are explicitly emphasized in the description.
- **Contrasting Intent Formulation**: A valid near-miss must invert the action predicate while keeping the object noun invariant:
  $$\text{Query} = \text{Verb}_{\text{competing}} + \text{Noun}_{\text{shared}}$$
  Example: For `csv-data-cleaner`, the positive query is "remove null rows from this CSV" ($\text{Verb}_{\text{clean}} + \text{CSV}$). The near-miss distractor is "write an Excel VLOOKUP formula for this CSV" ($\text{Verb}_{\text{formula}} + \text{CSV}$).

### Pass 2: Edge Cases & Failure Modes
- **The "Strawman Negative" Defect**: An evaluation author includes negative queries that share zero words with the skill (e.g. testing `docker-deployer` with "What is the capital of Peru?"). The skill easily passes, but the 100% negative accuracy is an illusion—the test never challenged the routing boundary.
- **False Negative Inversion**: A near-miss is authored so ambiguously that human engineers disagree on whether the skill should trigger. If a distractor's ground-truth label is contested, it introduces benchmark noise.
- **Keyword Starvation**: Stripping all shared keywords from a description to prevent false positives causes the skill to fail on legitimate positive queries (false negatives). Near-miss engineering balances the boundary rather than starving keywords.

### Pass 3: Expert Disagreements & Contrarian Views
- **Synthetic Hard Negatives (LLM Generated) vs Trace-Mined Hard Negatives**:
  - *Synthetic Proponents*: Use an LLM instructed to "generate 10 tricky queries that look like X but aren't".
  - *Empirical Systems Engineers (AgentSkills Standard)*: Find that synthetic negatives often rely on bizarre semantic riddles that real users never type. Trace-mined negatives—harvested from actual failed agent sessions where the model picked the wrong tool—reflect true user query distributions.

### Pass 4: Mathematical Formulation
Let $\mathcal{S}$ be the target skill and $\mathcal{S}'$ be a competitor skill.
Let $\text{Sim}_{\text{lex}}(q, \mathcal{S})$ denote lexical overlap (Jaccard similarity on nouns):
$$\text{Sim}_{\text{lex}}(q, \mathcal{S}) = \frac{|\text{Nouns}(q) \cap \text{Nouns}(\mathcal{S})|}{|\text{Nouns}(q) \cup \text{Nouns}(\mathcal{S})|}$$
A query $q^-$ is a valid Hard Negative iff:
$$\text{Sim}_{\text{lex}}(q^-, \mathcal{S}) \ge \theta_{\text{overlap}} \quad \text{and} \quad \text{GroundTruth}(q^-) \neq \mathcal{S}$$
Empirical Routing Margin ($M$):
$$M(\mathcal{S}, q^-) = P(\text{Route} \to \text{Alternative} \mid q^-) - P(\text{Route} \to \mathcal{S} \mid q^-) > 0$$

## 4. New-Information Rate Curve
- **Pass 0**: 5 baseline claims.
- **Pass 1**: 7 new claims / 12 total = 58.3% new info.
- **Pass 2**: 5 new claims / 17 total = 29.4% new info.
- **Pass 3**: 4 new claims / 21 total = 19.0% new info.
- **Pass 4**: 1 new claim / 22 total = 4.5% new info.
- **Pass 5**: 0 new claims / 22 total = 0.0% new info.

## 5. Saturation Verdict
- **Verdict**: `SATURATED-DEPTH`
- **Exhaustion Proof**: Lexical vector traps, contrasting intent formulas, strawman defects, and mathematical margin conditions fully established.
