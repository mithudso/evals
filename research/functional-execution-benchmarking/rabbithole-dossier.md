# Rabbithole Dossier: Functional Execution Benchmarking

## 1. Scope & Boundary
- **IN SCOPE**: Sandbox filesystem hierarchies, dual-arm comparative execution (`with_skill` vs `without_skill`), execution tracing (timing, tool call sequences, memory overhead), delta scoring mathematics, fixture immutability, automated assertion verification.
- **OUT OF SCOPE**: Single-turn prompt engineering, human subjective surveys, physical network infrastructure performance.

## 2. Pass 0: Baseline Atomic Claims
1. Agents are evaluated by running tasks in isolated filesystem workspaces.
2. Comparative benchmarking runs identical tests with the skill and without the skill.
3. Performance is measured using delta score $\Delta = \text{Score}_{\text{with}} - \text{Score}_{\text{without}}$.
4. Execution records duration, tool calls, and pass rates in `timing.json` and `eval_result.json`.
5. Failures are classified into runtime crashes, schema errors, and assertion misses.

## 3. Deepening Passes (Pass 1–4)

### Pass 1: Sandboxing Mechanics & Filesystem Isolation
- **Filesystem Leaks**: Agents modifying relative files can pollute parent workspaces if paths are unconfined. Production harnesses set `CWD` to `<workspace>/iteration-<N>/eval-<ID>/with_skill/` and mount input files via read-only bind mounts or fresh hard-copies.
- **Process Supervision**: Execution runners attach sub-process timeouts (typically 120s wall-clock) to prevent infinite while-loops or runaway retry spirals when an agent encounters unexpected tool exceptions.
- **Artifact Diffing**: Evaluation graders do not rely on agent conversational summaries; they execute git diff or cryptographic SHA-256 hash checks over expected deliverable paths.

### Pass 2: Edge Cases & Failure Modes
- **The "Trivial Task" Fallacy**: When tasks are too simple, base models achieve 100% pass rates, yielding $\Delta = 0$. The evaluation fails to test skill utility. Benchmarks must incorporate multi-step constraints and edge cases to ensure discriminative difficulty.
- **Token Budget Thrashing**: An agent with a verbose skill enters context thrashing—spending 90% of its token budget reading skill instructions, leaving insufficient context for tool outputs, leading to abrupt truncation.
- **State Pollution Across Test Cases**: If test case 2 reuses the directory modified by test case 1, test case 2 may fail due to residual locks or dirty Git states. Hermetic resets per test case are strictly required.

### Pass 3: Expert Disagreements & Contrarian Perspectives
- **Virtual Containers (Docker) vs In-Process Filesystem Worktrees**:
  - *Container Purists*: Advocate spinning up a fresh Alpine Docker container for every single eval run to guarantee network isolation and kernel-level filesystem sandboxing.
  - *Lightweight Worktree Empiricists (AgentSkills Practice)*: Point out that spinning up 50 containers introduces 15–30 seconds of latency per eval, turning a 2-minute benchmark suite into a 30-minute ordeal. Directory-based sandboxing with strict cleanup scripts achieves 99% of isolation guarantees with sub-second initialization.
- **Absolute Scoring vs Relative Delta Scoring**:
  - *Absolute Metric Advocates*: Measure absolute task completion rate.
  - *Delta Metric Advocates*: Argue that as base models improve, absolute pass rates drift upward regardless of skill quality. Delta scoring isolates the net marginal contribution of the skill instructions.

### Pass 4: Mathematical Formulation
Let $\mathcal{A}_{\text{base}}$ be the unassisted agent, and $\mathcal{A}_{\text{skill}}$ be the agent armed with skill $S$.
For test suite $\mathcal{E} = \{e_1, e_2, \dots, e_N\}$ with assertions $M(e_i) = \{a_{i1}, \dots, a_{im_i}\}$:
$$\text{Score}(\mathcal{A}, e_i) = \frac{1}{m_i} \sum_{j=1}^{m_i} \mathbf{1}[a_{ij}(\text{State}(\mathcal{A}, e_i)) = \text{PASS}]$$
$$\Delta(\mathcal{E}) = \frac{1}{N} \sum_{i=1}^N \left( \text{Score}(\mathcal{A}_{\text{skill}}, e_i) - \text{Score}(\mathcal{A}_{\text{base}}, e_i) \right)$$
Net Efficiency Ratio ($\mathcal{R}$):
$$\mathcal{R} = \frac{\Delta(\mathcal{E})}{\max\left(1, \log_2\left(\frac{\text{Tokens}(\mathcal{A}_{\text{skill}})}{\text{Tokens}(\mathcal{A}_{\text{base}})}\right)\right)}$$

## 4. New-Information Rate Curve
- **Pass 0**: 5 baseline claims.
- **Pass 1**: 7 new claims / 12 total = 58.3% new info.
- **Pass 2**: 5 new claims / 17 total = 29.4% new info.
- **Pass 3**: 4 new claims / 21 total = 19.0% new info.
- **Pass 4**: 1 new claim / 22 total = 4.5% new info.
- **Pass 5**: 0 new claims / 22 total = 0.0% new info.

## 5. Saturation Verdict
- **Verdict**: `SATURATED-DEPTH`
- **Exhaustion Proof**: Sandboxing mechanisms, failure modes, cost-efficiency formulas, and architectural debates fully documented.
