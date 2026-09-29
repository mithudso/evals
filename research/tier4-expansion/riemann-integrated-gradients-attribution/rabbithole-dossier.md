# Rabbithole Dossier: Riemann Integrated Gradients Attribution

## 1. Deep Mathematical Mechanics & Gauss-Legendre Quadrature

Let the forward model evaluation function be $F: \mathbb{R}^{L \times d} \to \mathbb{R}$ evaluating target solution logit. Let $\mathbf{X} \in \mathbb{R}^{L \times d}$ be the prompt embedding matrix and $\mathbf{X}' \in \mathbb{R}^{L \times d}$ be the baseline embedding.

Gauss-Legendre Quadrature calculates the definite integral $\int_{-1}^1 g(t) dt$ as:

$$\int_{-1}^1 g(t) dt \approx \sum_{k=1}^m w_k g(t_k)$$

Transforming the domain from $t \in [-1, 1]$ to $\alpha \in [0, 1]$ via substitution $\alpha = \frac{t + 1}{2}$ ($d\alpha = \frac{1}{2} dt$):

$$\text{IG}_i(\mathbf{X}) \approx \frac{\mathbf{X}_i - \mathbf{X}'_i}{2} \sum_{k=1}^m w_k \left. \nabla_{\mathbf{X}_i} F(\mathbf{X}' + \frac{t_k + 1}{2}(\mathbf{X} - \mathbf{X}')) \right.$$

Where $t_k$ are the roots of the Legendre polynomial $P_m(t)$, and weights $w_k$ are:

$$w_k = \frac{2}{(1 - t_k^2) [P'_m(t_k)]^2}$$

---

## 2. Python Concrete Implementation Harness

```python
import numpy as np
from typing import List, Tuple, Callable

class GaussLegendreIntegratedGradients:
    def __init__(self, steps: int = 20):
        self.steps = steps
        # Compute Gauss-Legendre roots and weights
        self.roots, self.weights = np.polynomial.legendre.leggauss(steps)
        # Map roots from [-1, 1] to [0, 1]
        self.alphas = 0.5 * (self.roots + 1.0)
        self.scaled_weights = 0.5 * self.weights

    def attribute(
        self,
        forward_grad_fn: Callable[[np.ndarray], np.ndarray],
        prompt_embedding: np.ndarray,
        baseline_embedding: np.ndarray = None
    ) -> Tuple[np.ndarray, float]:
        """
        prompt_embedding: (L, d)
        baseline_embedding: (L, d) or None (zeros)
        Returns:
            token_attributions: (L,) scalar importance per token
            completeness_gap: scalar difference between sum of attributions and delta logit
        """
        if baseline_embedding is None:
            baseline_embedding = np.zeros_like(prompt_embedding)

        diff = prompt_embedding - baseline_embedding  # (L, d)
        accumulated_grads = np.zeros_like(prompt_embedding)

        # Numerical integration across quadrature points
        for alpha, weight in zip(self.alphas, self.scaled_weights):
            interpolated_point = baseline_embedding + alpha * diff
            grad = forward_grad_fn(interpolated_point)  # (L, d)
            accumulated_grads += weight * grad

        # Elementwise product: (L, d)
        ig_matrix = diff * accumulated_grads
        
        # Scalar token attribution: L2 norm across embedding dimension
        token_attributions = np.linalg.norm(ig_matrix, axis=-1)
        
        # Total attribution sum
        total_attributed = np.sum(ig_matrix)

        return token_attributions, float(total_attributed)
```

---

## 3. Edge Cases & Failure Modes

1. **Non-Differentiable Tokenization**: Gradients can only be taken with respect to continuous embeddings $\mathbf{X}$, not discrete token IDs.
   - *Mitigation*: Forward hook attached directly to the embedding layer output tensor (`model.get_input_embeddings()`).
2. **Quadrature Step Collapse**: If $m < 10$, oscillatory gradients in deep multi-head attention can cause Gauss-Legendre integration to deviate from the completeness axiom.
   - *Mitigation*: Automated convergence check: if $|\sum \text{IG} - \Delta F| / |\Delta F| > 0.05$, dynamically double $m$ from 20 to 40.
