# Rabbithole Dossier: Delta Scoring and Capability Lift Analysis

## 1. Scope & Boundary
- **IN SCOPE**: Marginal lift mathematics, baseline control arms, dual-arm comparative execution, token overhead logarithmic penalties, statistical significance of score differences, net efficiency indexing.
- **OUT OF SCOPE**: Global macro-economic software ROI calculations, physical GPU power wattage tracking, human payroll impact studies.

## 2. Pass 0: Baseline Atomic Claims
1. Capability lift measures the marginal improvement of an assisted agent over an unassisted base model.
2. Raw scores conflate foundation model capabilities with skill instruction efficacy.
3. Delta score is calculated as $\Delta = \text{Score}_{\text{with}} - \text{Score}_{\text{without}}$.
4. A skill is certified only when $\Delta > 0$.
5. Skills that add excessive token overhead relative to quality gains are pruned.

## 3. Deepening Passes (Pass 1–4)

### Pass 1: Causal Attribution & The Control Arm
- **The Attribution Problem in Multi-Agent Systems**: In complex tasks, agent completion may be driven by superior base model reasoning rather than the skill instructions. Executing an unassisted control arm (`without_skill`) under identical inputs, temperature, and seeds isolates the specific treatment effect of the skill.
- **The Ceiling Effect**: When base models achieve >95% accuracy on a task, $\Delta$ is capped at <0.05. Measuring genuine lift requires designing "stress test" boundary conditions and edge cases that bring base model accuracy down to 20–40%, providing sufficient dynamic range for the skill to demonstrate substantial lift ($\Delta \ge 0.50$).

### Pass 2: Edge Cases & Failure Modes
- **Negative Lift ($\Delta < 0$) Due to Context Contamination**: A verbose skill fills 8,000 tokens of context with dense edge-case instructions. The base model becomes distracted by irrelevant rules, forgetting key user constraints it would have followed natively. This manifests as a negative delta score ($\Delta < 0$), signaling that the skill is actively degrading agent performance.
- **Trivial Redundancy ($\Delta \approx 0$)**: An engineer writes a skill instructing an agent on how to call a standard tool that the base model already knows how to use natively. Both arms score 100%, producing $\Delta = 0$. The skill adds token cost with zero marginal benefit.
- **High Variance Zero-Mean Lift**: The assisted arm scores 80% and the control arm scores 80%, but on completely different test cases. Overall $\Delta = 0$, but the skill introduced behavioral churn rather than systematic improvement.

### Pass 3: Expert Disagreements & Contrarian Perspectives
- **Pure Task Success vs Trajectory-Weighted Lift**:
  - *Outcome Purists*: Argue that only final deliverable correctness matters; if the task is completed, how many steps it took is irrelevant.
  - *Production Systems Architects*: Point out that an agent taking 15 tool calls and 12,000 tokens to complete a task that the base model solves in 3 tool calls and 1,500 tokens represents operational regression. Modern delta scoring incorporates trajectory penalties.

### Pass 4: Mathematical Formulation
Let $\mathcal{D}_{\text{test}} = \{(x_i, y_i)\}_{i=1}^N$ be the evaluation dataset.
Let $M(A, x_i) \in [0, 1]$ denote the assertion pass rate of agent $A$ on input $x_i$.
Treatment Agent $A_T = \text{Agent}(\text{Model}, \text{Skill})$, Control Agent $A_C = \text{Agent}(\text{Model}, \emptyset)$.
Sample Average Treatment Effect ($\widehat{\text{ATE}}$):
$$\widehat{\Delta} = \frac{1}{N}\sum_{i=1}^N \left( M(A_T, x_i) - M(A_C, x_i) \right)$$
Standard Error of the Delta:
$$\text{SE}(\widehat{\Delta}) = \sqrt{\frac{1}{N(N-1)}\sum_{i=1}^N \left( (M(A_T, x_i) - M(A_C, x_i)) - \widehat{\Delta} \right)^2}$$
Hypothesis Test for Capability Lift:
$$H_0: \Delta \le 0 \quad \text{vs} \quad H_1: \Delta > 0$$
Statistically Significant Lift requires:
$$t = \frac{\widehat{\Delta}}{\text{SE}(\widehat{\Delta})} > t_{\text{crit}} \quad (p < 0.05)$$

## 4. New-Information Rate Curve
- **Pass 0**: 5 baseline claims.
- **Pass 1**: 7 new claims / 12 total = 58.3% new info.
- **Pass 2**: 5 new claims / 17 total = 29.4% new info.
- **Pass 3**: 4 new claims / 21 total = 19.0% new info.
- **Pass 4**: 1 new claim / 22 total = 4.5% new info.
- **Pass 5**: 0 new claims / 22 total = 0.0% new info.

## 5. Saturation Verdict
- **Verdict**: `SATURATED-DEPTH`
- **Exhaustion Proof**: Ceiling effects, context contamination negatives, trajectory penalties, and hypothesis testing formulations fully derived.
