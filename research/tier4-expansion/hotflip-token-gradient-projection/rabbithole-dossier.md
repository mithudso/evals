# Rabbithole Dossier: HotFlip Token Gradient Projection

## 1. Deep Mathematical Mechanics & Tensor Formulation

Let input text be mapped to token indices $\mathbf{t} = (t_1, \dots, t_L)$ where $t_i \in \{1, \dots, V\}$. Let $\mathbf{E} \in \mathbb{R}^{V \times d}$ be the token embedding matrix. The sequence embedding tensor is:

$$\mathbf{X} = [\mathbf{E}_{t_1}; \mathbf{E}_{t_2}; \dots; \mathbf{E}_{t_L}] \in \mathbb{R}^{L \times d}$$

Let the target anchor embedding be $\mathbf{a}^* \in \mathbb{R}^d$ with $\|\mathbf{a}^*\|_2 = 1$. The cosine similarity objective to maximize toward the decision boundary is:

$$s(\mathbf{X}) = \frac{1}{L} \sum_{i=1}^L \frac{\mathbf{X}_i^T \mathbf{a}^*}{\|\mathbf{X}_i\|_2}$$

Compute the gradient of $s(\mathbf{X})$ with respect to token embedding $\mathbf{X}_i$:

$$\mathbf{g}_i = \nabla_{\mathbf{X}_i} s(\mathbf{X}) = \frac{1}{L} \left( \frac{\mathbf{a}^*}{\|\mathbf{X}_i\|_2} - \frac{(\mathbf{X}_i^T \mathbf{a}^*) \mathbf{X}_i}{\|\mathbf{X}_i\|_2^3} \right)$$

### Vocabulary-Wide HotFlip Directional Score

The linear approximation of the score change for replacing token $t_i$ with candidate token $j \in \{1, \dots, V\}$ is:

$$\Delta s_{i, j} \approx \mathbf{g}_i^T (\mathbf{E}_j - \mathbf{E}_{t_i})$$

In vectorized tensor notation across the entire vocabulary:

$$\mathbf{\Delta s}_i = \mathbf{E} \cdot \mathbf{g}_i - (\mathbf{E}_{t_i}^T \mathbf{g}_i) \mathbf{1}_V \in \mathbb{R}^V$$

---

## 2. Python Concrete Implementation Harness

```python
import numpy as np
from typing import List, Tuple, Dict

class HotFlipTokenProjector:
    def __init__(self, vocab_embeddings: np.ndarray, vocab_tokens: List[str]):
        """
        vocab_embeddings: Shape (V, d)
        vocab_tokens: List of length V
        """
        self.E = vocab_embeddings
        self.vocab = vocab_tokens
        self.token_to_id = {tok: idx for idx, tok in enumerate(vocab_tokens)}
        self.V, self.d = vocab_embeddings.shape

    def compute_gradient(self, token_ids: List[int], target_anchor: np.ndarray) -> np.ndarray:
        anchor = target_anchor / np.linalg.norm(target_anchor)
        X = self.E[token_ids]  # (L, d)
        L = len(token_ids)
        grads = np.zeros_like(X)
        
        for i in range(L):
            norm_x = np.linalg.norm(X[i])
            if norm_x > 1e-8:
                dot = np.dot(X[i], anchor)
                grads[i] = (1.0 / L) * (anchor / norm_x - (dot * X[i]) / (norm_x ** 3))
        return grads

    def best_replacement(
        self,
        token_ids: List[int],
        pos: int,
        target_anchor: np.ndarray,
        allowed_vocab_mask: np.ndarray = None
    ) -> Tuple[int, str, float]:
        """
        Finds the single best token replacement at position `pos` using HotFlip.
        """
        grads = self.compute_gradient(token_ids, target_anchor)
        g_i = grads[pos]  # (d,)
        curr_id = token_ids[pos]
        
        # Vectorized dot products: (V, d) @ (d,) -> (V,)
        delta_scores = np.dot(self.E, g_i) - np.dot(self.E[curr_id], g_i)
        
        if allowed_vocab_mask is not None:
            delta_scores[~allowed_vocab_mask] = -1e9
            
        best_id = int(np.argmax(delta_scores))
        return best_id, self.vocab[best_id], float(delta_scores[best_id])
```

---

## 3. Edge Cases & Failure Modes

1. **Subword Fragmentation Loop**: A flip substitutes an opening quotation mark or prefix subword (`"##ing"`), making downstream tokens syntactically illegal.
   - *Mitigation*: Whitelist only full-word token IDs during candidate filtering.
2. **Gradient Saturation in Softmax Layers**: If the surrogate model uses temperature-scaled cross-entropy, gradients vanishing on saturated logits prevent HotFlip from identifying meaningful swaps.
   - *Mitigation*: Compute gradients directly on un-normalized cosine projections rather than post-softmax probabilities.
