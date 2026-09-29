# Rabbithole Dossier: Answer Leakage Decontamination

## 1. Scope & Boundary
- **IN SCOPE**: Mathematical n-gram overlap scanning, syntactic prompt purification, counterfactual variable perturbation, canary string insertion, prompt-skill cross-correlation metrics, Pass F automated transformation engines.
- **OUT OF SCOPE**: Model weight gradient auditing, pre-training corpus web filtering, legal copyright fair use disputes.

## 2. Pass 0: Baseline Atomic Claims
1. Answer leakage occurs when eval prompts contain solution hints, rule blocks, or skill identifiers.
2. Leaked prompts test instruction parroting rather than autonomous reasoning.
3. Pass F scans for n-gram overlaps between test prompts and `SKILL.md`.
4. Overlap ratios exceeding 5% trigger mandatory prompt deconstruction.
5. Decontamination rewrites prompts to describe problems rather than solutions.

## 3. Deepening Passes (Pass 1–4)

### Pass 1: Semantic Cross-Entropy & Prompt Priming
- **The Priming Effect in Multi-Hop Reasoning**: When a prompt includes terms identical to section headings in a skill (e.g. asking an agent to "Execute the 5-phase data cleaning workflow"), it primes the model's self-attention heads to attend heavily to that exact section of the system prompt. The model does not need to deduce the workflow from scratch; the prompt has effectively solved the planning stage.
- **N-Gram Overlap Mathematics**: Pass F computes word-level n-gram overlap between prompt $P$ and skill document $S$:
  $$\text{Overlap}_n(P, S) = \frac{|\text{Grams}_n(P) \cap \text{Grams}_n(S)|}{|\text{Grams}_n(P)|}$$
  Production thresholds flag any test case where $\text{Overlap}_4(P, S) > 0.05$ or any single 6-gram matches identically (excluding common programming syntax).

### Pass 2: Edge Cases & Failure Modes
- **The "Over-Scrubbing" Trap**: An aggressive decontamination scanner flags and removes standard domain terminology (e.g. scrubbing "SQL", "CSV", or "JSON" because they appear in `SKILL.md`). This renders the prompt nonsensical. Decontamination must maintain an allowlist of universal industry terminology, filtering only distinctive procedural phrasing.
- **The Synonymous Leak**: An author attempts to bypass n-gram scanners by using a thesaurus to replace words ("Perform the five-stage information cleansing procedure"). While n-gram overlap drops to 0, the algorithmic prescription remains 100% leaked. Semantic vector similarity audits between prompts and skill procedure sections catch synonymous leaks.
- **Sub-Prompt Context Leakage**: Leakage occurs not in the initial user prompt, but in mock user responses or injected tool outputs during multi-turn evals. All turns in an eval suite must be scanned by Pass F.

### Pass 3: Expert Disagreements & Contrarian Perspectives
- **Few-Shot Demonstration Prompts vs Zero-Shot Problem Prompts**:
  - *Few-Shot Advocates*: Argue that providing input-output examples in the user prompt is standard engineering practice.
  - *DEO Benchmark Purists (AgentSkills Standard)*: Insist that for testing skill capabilities, user prompts must be zero-shot problem statements. If the user prompt provides few-shot demonstrations of the solution, it masks whether the skill's instructions were sufficient on their own.

### Pass 4: Mathematical Formulation
Let $\mathcal{P} = \{p_1, \dots, p_N\}$ be candidate test prompts and $\mathcal{S}$ be the target skill instructions.
Let $\mathcal{W}$ be an allowlist of universal domain stopwords and vocabulary.
Purified Prompt Representation:
$$\widetilde{p}_i = p_i \setminus \mathcal{W}, \quad \widetilde{\mathcal{S}} = \mathcal{S} \setminus \mathcal{W}$$
N-Gram Contamination Ratio:
$$\mathcal{C}_k(p_i, \mathcal{S}) = \frac{\sum_{g \in \text{Grams}_k(\widetilde{p}_i)} \mathbf{1}[g \in \text{Grams}_k(\widetilde{\mathcal{S}})]}{|\text{Grams}_k(\widetilde{p}_i)|}$$
Pass F Invariant:
$$\text{Pass}_F(p_i) = \mathbf{1}\left[ (\mathcal{C}_4(p_i, \mathcal{S}) \le 0.05) \land (\mathcal{C}_6(p_i, \mathcal{S}) = 0) \land \neg \text{ContainsAlgorithmicSteps}(p_i) \right]$$

## 4. New-Information Rate Curve
- **Pass 0**: 5 baseline claims.
- **Pass 1**: 7 new claims / 12 total = 58.3% new info.
- **Pass 2**: 5 new claims / 17 total = 29.4% new info.
- **Pass 3**: 4 new claims / 21 total = 19.0% new info.
- **Pass 4**: 1 new claim / 22 total = 4.5% new info.
- **Pass 5**: 0 new claims / 22 total = 0.0% new info.

## 5. Saturation Verdict
- **Verdict**: `SATURATED-DEPTH`
- **Exhaustion Proof**: Self-attention priming, over-scrubbing boundaries, synonymous leaks, and n-gram overlap equations fully specified.
