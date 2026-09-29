# Rabbithole Dossier: Semantic Vector Boundary Mining

## 1. Deep Mathematical Mechanics

Let the target skill anchor set be $\mathcal{A} = \{\mathbf{a}_1, \dots, \mathbf{a}_m\} \subset \mathbb{R}^d$ with $\|\mathbf{a}_i\|_2 = 1$. The decision score for input query embedding $\mathbf{q}$ is:

$$s(\mathbf{q}) = \max_{i \in \{1,\dots,m\}} \mathbf{q}^T \mathbf{a}_i$$

Let $\tau$ be the operational activation threshold. The objective of the boundary miner is to construct a negative candidate $\mathbf{q}^*$ such that:

$$\tau - \delta \le s(\mathbf{q}^*) < \tau \quad \text{where } \delta \in [0.01, 0.05]$$

subject to:

$$\mathcal{J}_{\text{oracle}}(\mathbf{q}^*) = 0$$

### Algorithmic Optimization via Spherical Projection

To synthesize such embeddings continuously before decoding to text:

1. **Initialization**: Select prototype negative $\mathbf{q}_0$ from a related, adjacent skill.
2. **Directional Step**: Compute gradient toward target anchor $\mathbf{a}^* = \arg\max_{\mathbf{a}_i} \mathbf{q}_k^T \mathbf{a}_i$:
   $$\mathbf{g}_k = \mathbf{a}^* - (\mathbf{q}_k^T \mathbf{a}^*) \mathbf{q}_k$$
3. **Spherical Update**: Step along the great circle on $\mathcal{S}^{d-1}$:
   $$\mathbf{q}_{k+1} = \cos(\eta) \mathbf{q}_k + \sin(\eta) \frac{\mathbf{g}_k}{\|\mathbf{g}_k\|_2}$$
4. **Boundary Termination**: Stop when $\mathbf{q}_{k+1}^T \mathbf{a}^* \in [\tau - \delta, \tau)$.
5. **Discrete Decoding**: Nearest-neighbor k-NN projection or beam-search diffusion mapping from continuous embedding $\mathbf{q}^*$ back to discrete natural language tokens.

---

## 2. Python Concrete Implementation Harness

```python
import numpy as np
from typing import List, Dict, Tuple

class SemanticBoundaryMiner:
    def __init__(self, target_anchor: np.ndarray, threshold: float = 0.85, delta: float = 0.03):
        self.target_anchor = target_anchor / np.linalg.norm(target_anchor)
        self.threshold = threshold
        self.delta = delta

    def score(self, vec: np.ndarray) -> float:
        norm = np.linalg.norm(vec)
        if norm == 0:
            return 0.0
        return float(np.dot(vec / norm, self.target_anchor))

    def is_in_boundary_strip(self, vec: np.ndarray) -> bool:
        s = self.score(vec)
        return (self.threshold - self.delta) <= s < self.threshold

    def project_boundary_step(self, vec: np.ndarray, step_size: float = 0.02, max_iter: int = 50) -> np.ndarray:
        q = vec / np.linalg.norm(vec)
        for _ in range(max_iter):
            current_score = self.score(q)
            if (self.threshold - self.delta) <= current_score < self.threshold:
                return q
            
            # Gradient along great circle toward target anchor
            grad = self.target_anchor - (np.dot(q, self.target_anchor)) * q
            grad_norm = np.linalg.norm(grad)
            if grad_norm < 1e-6:
                break
            grad_dir = grad / grad_norm
            
            # If below threshold, move closer; if above, move away
            direction = 1.0 if current_score < self.threshold else -1.0
            theta = direction * step_size
            q = np.cos(theta) * q + np.sin(theta) * grad_dir
            q = q / np.linalg.norm(q)
            
        return q

    def audit_eval_suite(self, negatives: List[Dict[str, any]]) -> Dict[str, float]:
        """
        Calculates boundary coverage metrics for a suite's negative test cases.
        """
        scores = [self.score(item["embedding"]) for item in negatives]
        in_strip = [s for s in scores if (self.threshold - self.delta) <= s < self.threshold]
        leaks = [s for s in scores if s >= self.threshold]
        
        return {
            "total_negatives": len(negatives),
            "strip_coverage_ratio": len(in_strip) / max(len(negatives), 1),
            "false_positive_leak_ratio": len(leaks) / max(len(negatives), 1),
            "mean_cosine_proximity": float(np.mean(scores)) if scores else 0.0,
            "max_cosine_negative": float(np.max(scores)) if scores else 0.0
        }
```

---

## 3. Edge Cases & Failure Modes

1. **Adversarial Token Collapse (Gibberish Prompts)**: Token-level gradient descent can yield ungrammatical token strings (`"git merge docker k8s optimize!"`) that achieve high vector similarity while lacking human semantic coherence.
   - *Mitigation*: Hard perplexity filter with an external language model ($P(x) \le 45.0$).
2. **Oracle Invalidation Drift**: When stepping toward the target embedding, the prompt may cross the latent semantic threshold before the vector threshold, causing the human user to genuinely desire the skill.
   - *Mitigation*: Dual-prompt validation: run prompt through full tool-calling agent. If tool is called, discard as false negative.
