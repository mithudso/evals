# Rabbithole Dossier: Eval-Driven Iteration Loop

## 1. Scope & Boundary
- **IN SCOPE**: Multi-iteration loop mechanics, versioned workspace transitions (`iteration-1` -> `iteration-2`), flakiness standard deviation formulas, champion-challenger promotion gating invariants, golden regression suites, early stopping criteria.
- **OUT OF SCOPE**: Global base-model pretraining loss curves, reinforcement learning reward model architecture, human crowdsourcing platform operations.

## 2. Pass 0: Baseline Atomic Claims
1. Skills are improved iteratively using benchmark feedback loops.
2. An iteration loop executes baseline audit, benchmark, grading, diagnosis, and patching.
3. Flaky evaluations oscillate across repeated runs without code changes.
4. Champion-challenger testing compares a new skill revision against the current production baseline.
5. Promotion requires higher overall score ($\Delta > 0$) and zero golden regression failures.

## 3. Deepening Passes (Pass 1–4)

### Pass 1: Convergence Mechanics & Phase Transitions
- **State Checkpointing**: Each iteration creates an immutable snapshot directory `<skill>-workspace/iteration-<N>/` containing the exact `SKILL.md` text, the executed test suite, all raw trace files, and the grader scorecard. Reverting a failed iteration is an atomic symlink or file copy.
- **Minimal Diff Discipline**: When diagnosis identifies a failed assertion, prompt engineers must not rewrite the skill. Wholesale rewrites disrupt prompt attention structures that were supporting passing test cases, causing broad regression cascades. All patches must be surgical: adding a single constraint clause, clarifying an ambiguous format rule, or inserting a missing negative bound.
- **Convergence Gating**: The iteration loop terminates automatically when:
  1. $\text{PassRate} = 1.0$ (complete saturation).
  2. $|\Delta_n - \Delta_{n-1}| < 0.02$ across two consecutive iterations (asymptotic plateau).
  3. $n \ge n_{\text{max}}$ (budget exhaustion).

### Pass 2: Edge Cases & Failure Modes
- **The "Overfitting Trap"**: Continuously patching a prompt to pass a static 10-case evaluation suite leads to prompt memorization, where the agent learns brittle hacks tailored to the exact test prompts rather than generalized capability. Defense: partition a held-out test suite evaluated only after convergence.
- **Flakiness Contamination**: An unstable assertion with standard deviation $\sigma = 0.50$ randomly fails on 50% of runs. If a developer attempts to fix this by modifying `SKILL.md`, they waste engineering iterations chasing model noise. Flaky assertions must be quarantined, debugged for prompt ambiguity, and converted to deterministic checks before resuming prompt iteration.
- **Negative Delta Collapse**: A candidate patch improves a difficult edge case by +5%, but breaks a fundamental convention, causing a -20% collapse across the golden baseline. Champion-challenger gates catch this immediately and reject the patch.

### Pass 3: Expert Disagreements & Contrarian Perspectives
- **Autonomous Prompt Compilers (DSPy) vs Human-Guided Iteration Loops**:
  - *Autonomous Prompt Optimizers*: Argue that LLMs evaluating LLMs with gradient-free search (e.g. MIPROv2, BootstrapFewShot) can discover prompt formulations humans would never conceive.
  - *Empirical Agent Engineers (AgentSkills Standard)*: Note that compiler-generated prompts become inscrutable, sprawling prompt blobs that are impossible for human engineers to maintain, audit, or safely edit. Eval-driven iteration with structured human/LLM surgical patches maintains legible, modular, documentation-grade `SKILL.md` files.
- **Zero-Tolerance Regression vs Soft Pareto Gating**:
  - *Zero-Tolerance Purists*: Insist zero regressions on golden tests, ever.
  - *Pareto Advocates*: Argue that fixing a severe security vulnerability might justify a temporary 2% drop in stylistic formatting adherence.

### Pass 4: Mathematical Formulation
Let $\mathcal{G}$ be the golden regression suite with $M$ assertions.
Let $s_j(v)$ be the binary score of assertion $j$ under version $v$.
Golden Invariant:
$$\forall j \in \mathcal{G}, \quad s_j(v_{\text{challenger}}) \ge s_j(v_{\text{champion}})$$
Flakiness Variance across $K$ trials:
$$\bar{s}_{ij} = \frac{1}{K}\sum_{k=1}^K s_{ijk}, \quad \sigma_{ij}^2 = \frac{1}{K-1}\sum_{k=1}^K (s_{ijk} - \bar{s}_{ij})^2$$
Flaky Quarantine Rule:
$$\text{If } \sigma_{ij} > \tau_{\text{noise}}, \quad \text{Quarantine}(A_{ij})$$
Promotion Decision:
$$\text{Promote}(v_{\text{challenger}}) = \mathbf{1}\left[ \left(\Delta_{\text{overall}} > 0\right) \land \left(\sum_{j \in \mathcal{G}} \max(0, s_j(v_{\text{champ}}) - s_j(v_{\text{chall}})) = 0\right) \right]$$

## 4. New-Information Rate Curve
- **Pass 0**: 5 baseline claims.
- **Pass 1**: 7 new claims / 12 total = 58.3% new info.
- **Pass 2**: 5 new claims / 17 total = 29.4% new info.
- **Pass 3**: 4 new claims / 21 total = 19.0% new info.
- **Pass 4**: 1 new claim / 22 total = 4.5% new info.
- **Pass 5**: 0 new claims / 22 total = 0.0% new info.

## 5. Saturation Verdict
- **Verdict**: `SATURATED-DEPTH`
- **Exhaustion Proof**: Loop mechanics, checkpointing, overfitting traps, Pareto controversies, and mathematical gating formulas fully specified.
