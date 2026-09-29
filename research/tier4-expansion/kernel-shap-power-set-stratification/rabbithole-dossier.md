# Rabbithole Dossier: Kernel SHAP Power Set Stratification

## 1. Deep Mathematical Mechanics & Regression Solver

Let $N$ denote the number of clauses, and let $\mathcal{S}$ denote a sampled set of $M$ binary vectors $\mathbf{z}_k \in \{0, 1\}^N$. Let $v(\mathbf{z}_k)$ be the empirical evaluation score.

Let $\mathbf{Z} \in \mathbb{R}^{M \times (N+1)}$ be the design matrix where the first column is 1 (for intercept $\phi_0$), and the remaining $N$ columns are the binary inclusion indicators $\mathbf{z}_k$.

The diagonal weight matrix $\mathbf{W} \in \mathbb{R}^{M \times M}$ has elements:

$$\mathbf{W}_{k,k} = \pi(\mathbf{z}_k) = \frac{N - 1}{\binom{N}{|z_k|} |z_k| (N - |z_k|)}$$

For the boundary cases $\mathbf{z} = \mathbf{0}$ and $\mathbf{z} = \mathbf{1}$, $\pi(\mathbf{z}) = \infty$. To avoid numerical singularity, we enforce boundary constraints analytically:

$$\phi_0 = v(\mathbf{0})$$
$$\sum_{i=1}^N \phi_i = v(\mathbf{1}) - v(\mathbf{0}) = \Delta_{\text{total}}$$

Subtracting $\phi_0$ and transforming $\mathbf{y}_k^* = v(\mathbf{z}_k) - \phi_0$, the constrained weighted regression solves for $\mathbf{\phi} \in \mathbb{R}^N$:

$$\mathbf{\phi} = (\mathbf{Z}_{\text{sub}}^T \mathbf{W} \mathbf{Z}_{\text{sub}} + \lambda \mathbf{I})^{-1} \mathbf{Z}_{\text{sub}}^T \mathbf{W} \mathbf{y}^*$$

---

## 2. Python Concrete Implementation Harness

```python
import numpy as np
import scipy.special
from typing import List, Dict, Callable

class StratifiedKernelSHAP:
    def __init__(self, num_clauses: int, eval_fn: Callable[[np.ndarray], float]):
        self.N = num_clauses
        self.eval_fn = eval_fn

    def _shapley_kernel_weight(self, k: int) -> float:
        if k == 0 or k == self.N:
            return 1e6  # Large finite proxy for boundary anchor
        comb = scipy.special.comb(self.N, k)
        return (self.N - 1.0) / (comb * k * (self.N - k))

    def run_stratified_attribution(self, total_samples: int = 256) -> Dict[str, any]:
        # Always evaluate boundary anchors
        v_null = self.eval_fn(np.zeros(self.N, dtype=int))
        v_full = self.eval_fn(np.ones(self.N, dtype=int))
        delta_total = v_full - v_null

        # Deterministically evaluate singletons (k=1) and leave-one-out (k=N-1)
        samples = []
        weights = []
        targets = []

        # k = 1
        for i in range(self.N):
            z = np.zeros(self.N, dtype=int)
            z[i] = 1
            samples.append(z)
            weights.append(self._shapley_kernel_weight(1))
            targets.append(self.eval_fn(z) - v_null)

        # k = N - 1
        for i in range(self.N):
            z = np.ones(self.N, dtype=int)
            z[i] = 0
            samples.append(z)
            weights.append(self._shapley_kernel_weight(self.N - 1))
            targets.append(self.eval_fn(z) - v_null)

        # Stratified sampling for middle cardinalities 2 <= k <= N - 2
        remaining_budget = max(0, total_samples - 2 * self.N)
        middle_ks = list(range(2, self.N - 1))
        
        if middle_ks and remaining_budget > 0:
            strata_weights = [self._shapley_kernel_weight(k) * scipy.special.comb(self.N, k) for k in middle_ks]
            total_sw = sum(strata_weights)
            allocations = [int(round(remaining_budget * (sw / total_sw))) for sw in strata_weights]
            
            for k, count in zip(middle_ks, allocations):
                for _ in range(count):
                    z = np.zeros(self.N, dtype=int)
                    chosen = np.random.choice(self.N, size=k, replace=False)
                    z[chosen] = 1
                    samples.append(z)
                    weights.append(self._shapley_kernel_weight(k))
                    targets.append(self.eval_fn(z) - v_null)

        Z = np.array(samples)
        W = np.diag(weights)
        y = np.array(targets)

        # Weighted least squares with ridge regularization
        ridge = 1e-5 * np.eye(self.N)
        A = Z.T @ W @ Z + ridge
        b = Z.T @ W @ y
        phi = np.linalg.solve(A, b)

        # Normalize to enforce exact efficiency constraint sum(phi) = delta_total
        phi = phi * (delta_total / max(np.sum(phi), 1e-12))

        return {
            "v_null": float(v_null),
            "v_full": float(v_full),
            "delta_total": float(delta_total),
            "shapley_attributions": phi.tolist(),
            "samples_evaluated": len(samples) + 2
        }
```

---

## 3. Edge Cases & Failure Modes

1. **Ill-Conditioned Normal Matrix**: If two clauses are strongly collinear (always present together in DAG templates), $\mathbf{Z}^T \mathbf{W} \mathbf{Z}$ becomes rank-deficient.
   - *Mitigation*: Dynamic SVD pseudo-inverse with singular value truncation at threshold $\sigma_i < 10^{-4}$.
2. **Negative Lift Normalization Distortion**: If $\Delta_{\text{total}} \le 0$ (the skill actively degrades the base model), proportional re-scaling can invert signs.
   - *Mitigation*: Unconstrained additive shift rather than multiplicative rescaling when $\Delta_{\text{total}} \le 0$.
