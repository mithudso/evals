# Rabbithole Dossier: Objective Assertion Engineering

## 1. Scope & Boundary
- **IN SCOPE**: Deterministic verification algorithms, regex boundary matching, JSON Schema draft-07/2020-12 validation, AST syntax checks, negative constraint tripwires, mathematical count reconciliation, binary indicator functions.
- **OUT OF SCOPE**: Subjective human sentiment labeling, open-ended conversational evaluation, pure stylistic prose reviews.

## 2. Pass 0: Baseline Atomic Claims
1. Evaluation assertions must be objective, deterministic, and verifiable.
2. Assertions fall into structural, schema, content, negative bound, and count categories.
3. Subjective vibe criteria ("looks good") introduce high inter-rater variance.
4. Negative assertions verify the explicit absence of hallucinations and side-effects.
5. Graders output strictly boolean 1 (Pass) or 0 (Fail).

## 3. Deepening Passes (Pass 1–4)

### Pass 1: Mechanism & Parsing Dynamics
- **Syntactic Robustness vs Exact Matching**: Naive assertions testing for exact string equality fail when models introduce innocuous whitespace, trailing newlines, or Unicode quotation marks (`“` vs `"`). Objective assertion engineering enforces normalization pipelines: stripping trailing whitespace, standardizing line breaks (`\r\n` -> `\n`), and compiling case-insensitive multiline regex with word boundaries (`\b`).
- **Schema Validation Engines**: High-performance schema grading evaluates JSON payloads against JSON Schema standards using validators that isolate semantic defects (missing required keys, type mismatches, out-of-range scalars) and return machine-readable error paths (e.g. `root.findings[2].severity`).
- **AST Parsing for Code Artifacts**: When evaluating code-generation skills, assertions do not regex search source text; they invoke language parsers (e.g. Python `ast.parse` or Babel parser) to verify that generated scripts compile cleanly without syntax errors and declare required classes and methods.

### Pass 2: Edge Cases & Failure Modes
- **The Empty Artifact Loophole**: An assertion checking for the absence of `ERROR` trivially passes if the agent outputs an empty file. Negative bounding assertions must always be paired with positive structural assertions (e.g. "File exists AND size > 100 bytes AND contains zero `ERROR` tokens").
- **Tautological Assertions**: An assertion that tests a condition guaranteed to be true by the base environment (e.g. checking that a directory exists when the test runner created it) provides false positive confidence.
- **Header-Body Drift (Count Desynchronization)**: Large language models frequently output summary lines ("Here are the 5 critical vulnerabilities:") followed by only 3 or 4 listed items due to mid-generation attention drift. Reconciling count assertions programmatically parse both the summary integer and the list item count, failing if $N_{\text{header}} \neq N_{\text{items}}$.

### Pass 3: Expert Disagreements & Contrarian Views
- **LLM-as-a-Judge vs Deterministic Programmatic Checks**:
  - *LLM-Judge Proponents*: Claim modern frontier models (e.g. GPT-4o, Claude 3.5 Sonnet) can evaluate subtle nuances and reasoning steps that regex or schemas cannot capture.
  - *Deterministic Engineers (AgentSkills Practice)*: Point out that LLM judges suffer from position bias (preferring whichever output appears first), verbosity bias (favoring longer text regardless of accuracy), and non-zero drift across model updates. If an evaluation cannot be expressed as code, schema, or regex, the specification itself is underspecified.
- **Strict Binary vs Partial Credit**:
  - *Partial Credit Advocates*: Use continuous scores between 0.0 and 1.0 to reward near-misses.
  - *Binary Gating Advocates*: Insist that in production systems, a malformed JSON payload or broken API call is 100% defective; partial credit masks critical runtime bugs.

### Pass 4: Mathematical Formulation
Let $\mathcal{O}$ be the artifact output produced by the agent.
An assertion suite is a set of deterministic predicates $\{P_1, P_2, \dots, P_m\}$ where:
$$P_j : \mathcal{O} \to \{0, 1\}$$
Composite Assertion Score:
$$S(\mathcal{O}) = \frac{1}{m} \sum_{j=1}^m P_j(\mathcal{O})$$
Strict Conjunctive Gating:
$$G_{\text{strict}}(\mathcal{O}) = \prod_{j=1}^m P_j(\mathcal{O}) \in \{0, 1\}$$
For count reconciliation with declared count $C(\mathcal{O})$ and extracted items $I(\mathcal{O})$:
$$P_{\text{count}}(\mathcal{O}) = \mathbf{1}[C(\mathcal{O}) = |I(\mathcal{O})|]$$

## 4. New-Information Rate Curve
- **Pass 0**: 5 baseline claims.
- **Pass 1**: 7 new claims / 12 total = 58.3% new info.
- **Pass 2**: 5 new claims / 17 total = 29.4% new info.
- **Pass 3**: 4 new claims / 21 total = 19.0% new info.
- **Pass 4**: 1 new claim / 22 total = 4.5% new info.
- **Pass 5**: 0 new claims / 22 total = 0.0% new info.

## 5. Saturation Verdict
- **Verdict**: `SATURATED-DEPTH`
- **Exhaustion Proof**: Parsing dynamics, failure edge cases, count reconciliation math, and judge controversies fully resolved.
