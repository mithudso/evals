# Rabbithole Dossier: Champion-Challenger Canary Gating

## 1. Scope & Boundary
- **IN SCOPE**: Zero-regression invariant math, golden dataset versioning, canary traffic weighting, shadow execution pipelines, automated rollback tripwires, context overhead bounding, trace-to-eval promotion.
- **OUT OF SCOPE**: Kubernetes cluster ingress load-balancing hardware, BGP network peering, manual sales team user interviews.

## 2. Pass 0: Baseline Atomic Claims
1. The Champion is the validated production skill; the Challenger is the candidate revision.
2. The Challenger must pass all golden regression cases with zero exceptions.
3. Offline evaluation precedes shadow and canary deployments.
4. Production failures are converted into new golden test cases.
5. Automated tripwires trigger rollbacks upon canary failure.

## 3. Deepening Passes (Pass 1–4)

### Pass 1: The Non-Regression Invariant & Pareto Boundaries
- **Conjunctive Zero-Regression Invariant**: In traditional ML, models are deployed if average test loss decreases, even if a few specific examples regress. For agent skills, this is unacceptable: if an agent previously knew how to format dates correctly in a finance pipeline, a prompt update that improves tabular formatting but regresses date handling breaks existing production workflows. The release gate enforces a strict non-regression invariant:
  $$\forall t \in \mathcal{G}_{\text{golden}}, \quad \mathbf{1}[\text{Pass}(v_{\text{challenger}}, t)] \ge \mathbf{1}[\text{Pass}(v_{\text{champion}}, t)]$$
- **The Challenger Promotion Gauntlet**: A candidate must satisfy three simultaneous conditions:
  1. $\Delta_{\text{golden}} \ge 0$ (zero regressions on core tasks).
  2. $\Delta_{\text{frontier}} > 0$ (measurable lift on newly introduced tasks).
  3. $\Delta_{\text{cost}} \le 1.20$ (token and duration overhead bounded to $< 20\%$).

### Pass 2: Edge Cases & Failure Modes
- **The "Overfitted Golden Net"**: If a golden dataset never evolves, developers tune prompts to memorize the static cases. Over time, the model's generalized capability degrades while golden scores remain 100%. Defense: Pair the frozen golden set with dynamic canary fuzzing and held-out validation sets.
- **Canary Silent Drift**: A challenger passes offline tests, but in canary deployment, users experience a 40% increase in conversational turn-count (the agent requires more clarification turns to reach the same result). Canary monitoring must track trajectory length and turn count, not just terminal error codes.
- **Flaky Regression False Alarms**: A non-deterministic assertion in the golden set fails randomly during a challenger CI run, blocking a valid deployment. Golden datasets must be rigorously de-flaked: any assertion with $\sigma > 0$ must be quarantined until deterministic.

### Pass 3: Expert Disagreements & Contrarian Views
- **Shadow Mode vs Immediate Canary Rollout**:
  - *Fast Iterators*: Prefer deploying directly to 5% canary traffic to get real user feedback quickly.
  - *High-Assurance Engineers (AgentSkills Standard)*: Shadow mode is essential for autonomous agents because agents execute real actions (API calls, file modifications). Running a broken agent on 5% of real users can delete live customer data; shadow mode runs the candidate asynchronously against read-only mirrors with zero user risk.

### Pass 4: Mathematical Formulation
Let $\mathcal{G} = \{t_1, \dots, t_M\}$ be the golden dataset.
Let $\mathcal{C}_{\text{cand}}$ and $\mathcal{C}_{\text{prod}}$ be candidate and production skill versions.
Regression Indicator:
$$\mathcal{R}(\mathcal{C}_{\text{cand}}, \mathcal{C}_{\text{prod}}) = \sum_{j=1}^M \max\left(0, \text{Score}(t_j \mid \mathcal{C}_{\text{prod}}) - \text{Score}(t_j \mid \mathcal{C}_{\text{cand}})\right)$$
Promotion Gate:
$$\text{Deployable}(\mathcal{C}_{\text{cand}}) = \mathbf{1}\left[ (\mathcal{R} = 0) \land (\Delta_{\text{new}} > 0) \land \left(\frac{\text{Tokens}(\mathcal{C}_{\text{cand}})}{\text{Tokens}(\mathcal{C}_{\text{prod}})} \le 1.20\right) \right]$$

## 4. New-Information Rate Curve
- **Pass 0**: 5 baseline claims.
- **Pass 1**: 7 new claims / 12 total = 58.3% new info.
- **Pass 2**: 5 new claims / 17 total = 29.4% new info.
- **Pass 3**: 4 new claims / 21 total = 19.0% new info.
- **Pass 4**: 1 new claim / 22 total = 4.5% new info.
- **Pass 5**: 0 new claims / 22 total = 0.0% new info.

## 5. Saturation Verdict
- **Verdict**: `SATURATED-DEPTH`
- **Exhaustion Proof**: Non-regression invariants, shadow execution mechanics, canary drift indicators, and promotion gate formulas fully codified.
