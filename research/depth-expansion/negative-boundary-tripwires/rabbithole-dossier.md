# Rabbithole Dossier: Negative Boundary Tripwires

## 1. Scope & Boundary
- **IN SCOPE**: Multiplicative circuit-breaker assertions, honeypot canary detection, filesystem mutation bounding, placeholder text regex filters, forbidden token repulsion, immediate execution halts.
- **OUT OF SCOPE**: Global network firewall hardware routing, physical data center intrusion detection, human social engineering defense.

## 2. Pass 0: Baseline Atomic Claims
1. Negative boundary tripwires test for prohibited behaviors and artifacts.
2. A single tripped negative boundary fails the entire test case.
3. Tripwires verify absence of placeholders, AI-isms, and unauthorized file mutations.
4. Honeypot files placed in workspaces expose rogue tool exploration.
5. Invariants are evaluated deterministically against filesystem state.

## 3. Deepening Passes (Pass 1–4)

### Pass 1: Multiplicative Circuit-Breaker Invariants
- **Additive Failure vs Multiplicative Zeroing**: In standard grading, satisfying 9 out of 10 assertions yields a 90% score. But if the 10th assertion was "Did not overwrite production database credentials," awarding 90% is dangerously misleading. Negative tripwires function as a boolean multiplier:
  $$S = \left(\frac{1}{M}\sum_{i=1}^M A^+_i\right) \times \prod_{j=1}^K \left(1 - T^-_j\right)$$
  Where $T^-_j \in \{0, 1\}$ is 1 if tripwire $j$ is violated. Any violation zeroes the entire composite grade.
- **Immediate Trajectory Termination**: In live execution environments, tripwire hooks intercept tool calls at runtime. If an agent executes `rm -rf` or attempts to edit a protected configuration file, the process raises an uncatchable `TripwireViolationException`, terminating the trial immediately to prevent environmental corruption.

### Pass 2: Edge Cases & Failure Modes
- **The "Over-Sensitive Tripwire"**: A negative assertion banning words like "error" causes false positive test failures when the agent correctly outputs a debugging log explaining an error. Solution: Anchor tripwires to structural contexts (e.g. banning `^ERROR:` or `Traceback (most recent call last):` rather than the bare substring `"error"`).
- **The Silent Bypass (Whitespace Obfuscation)**: A model evades a banned token filter for `TODO` by outputting `T O D O` or `T-O-D-O`. Robust regex tripwires enforce normalized token cleaning: `\bT[\s_-]*O[\s_-]*D[\s_-]*O\b`.
- **Honeypot Lure False Positives**: Placing a honeypot file whose name collides with a standard tool expectation (e.g. naming the honeypot `package.json` in a Node project) unjustly penalizes legitimate dependency inspection. Honeypot names must be explicitly out-of-scope (e.g. `secret_vault_keys.json`).

### Pass 3: Expert Disagreements & Contrarian Perspectives
- **Soft Warning Annotations vs Hard Circuit Breaking**:
  - *Developer Experience Advocates*: Prefer soft warnings so engineers can see partial progress on features while fixing security boundary violations.
  - *Safety and Reliability Engineers (AgentSkills Standard)*: Insist on hard circuit breakers. In agentic production systems, a security boundary breach or unrequested deletion is catastrophic; releasing an agent that passes 99% of tasks while occasionally overwriting critical state is untenable.

### Pass 4: Mathematical Formulation
Let $\mathcal{T} = (\tau_1, \tau_2, \dots, \tau_T)$ be the execution trajectory of tool calls.
Let $\mathcal{O}$ be the set of created/modified filesystem artifacts.
Tripwire Predicates:
$$T_{\text{fs}}(\mathcal{O}) = \mathbf{1}[\exists f \in \mathcal{O} \text{ s.t. } f \notin \text{AllowedPaths}]$$
$$T_{\text{honeypot}}(\mathcal{T}) = \mathbf{1}[\exists \tau_t \text{ s.t. } \text{Target}(\tau_t) \in \text{HoneypotPaths}]$$
$$T_{\text{banned}}(\mathcal{O}) = \mathbf{1}[\exists f \in \mathcal{O} \text{ s.t. } \text{RegexMatch}(f, \mathcal{R}_{\text{prohibited}})]$$
Master Safety Gating Function:
$$G_{\text{safety}}(\mathcal{T}, \mathcal{O}) = 1 - \max\left(T_{\text{fs}}(\mathcal{O}), T_{\text{honeypot}}(\mathcal{T}), T_{\text{banned}}(\mathcal{O})\right) \in \{0, 1\}$$

## 4. New-Information Rate Curve
- **Pass 0**: 5 baseline claims.
- **Pass 1**: 7 new claims / 12 total = 58.3% new info.
- **Pass 2**: 5 new claims / 17 total = 29.4% new info.
- **Pass 3**: 4 new claims / 21 total = 19.0% new info.
- **Pass 4**: 1 new claim / 22 total = 4.5% new info.
- **Pass 5**: 0 new claims / 22 total = 0.0% new info.

## 5. Saturation Verdict
- **Verdict**: `SATURATED-DEPTH`
- **Exhaustion Proof**: Multiplicative zeroing math, token normalization regex, honeypot safety mechanics, and trajectory circuit breakers fully formalized.
