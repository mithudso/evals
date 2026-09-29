# Rabbithole Dossier: Causal Shapley Token Attribution

## 1. Deep Mathematical Mechanics

Let the prompt under evaluation be partitioned into $K$ disjoint semantic blocks $\mathcal{P} = \{b_1, b_2, \dots, b_K\}$. For a subset coalition $S \subseteq \{1, \dots, K\}$, define prompt assembly operator:

$$\mathcal{T}(S) = \bigoplus_{j \in S} b_j$$

For a benchmark task set $\mathcal{D} = \{(x_k, y_k)\}_{k=1}^M$, the characteristic payoff function is:

$$v(S) = \frac{1}{M} \sum_{k=1}^M \mathbb{I}\left( \text{Agent}(\mathcal{T}(S), x_k) = y_k \right)$$

### Unbiased Monte Carlo Permutation Estimator

When exact evaluation of $2^K$ coalitions is prohibitive, we sample $P$ random permutations $\pi \in \mathfrak{S}_K$. For permutation $\pi$, let $\text{Pre}_i(\pi)$ denote the set of blocks preceding block $i$ in $\pi$:

$$\text{Pre}_i(\pi) = \{j \in \{1,\dots,K\} \mid \pi(j) < \pi(i)\}$$

The marginal contribution of block $i$ under permutation $\pi$ is:

$$\Delta_i(\pi) = v(\text{Pre}_i(\pi) \cup \{i\}) - v(\text{Pre}_i(\pi))$$

The Monte Carlo Shapley estimate $\hat{\phi}_i$ is:

$$\hat{\phi}_i = \frac{1}{P} \sum_{p=1}^P \Delta_i(\pi_p)$$

Variance of the estimator decays as $O(1/P)$, providing statistical confidence bounds for pruning decisions.

---

## 2. Python Concrete Implementation Harness

```python
import itertools
import random
from typing import List, Dict, Callable

class PromptShapleyAttributor:
    def __init__(self, blocks: Dict[str, str], eval_fn: Callable[[str], float]):
        self.block_names = list(blocks.keys())
        self.blocks = blocks
        self.eval_fn = eval_fn
        self.cache: Dict[tuple, float] = {}

    def _assemble_prompt(self, coalition: tuple) -> str:
        return "\n\n".join(self.blocks[name] for name in self.block_names if name in coalition)

    def _evaluate_coalition(self, coalition: tuple) -> float:
        sorted_coalition = tuple(sorted(coalition))
        if sorted_coalition not in self.cache:
            prompt = self._assemble_prompt(sorted_coalition)
            self.cache[sorted_coalition] = self.eval_fn(prompt)
        return self.cache[sorted_coalition]

    def compute_exact_shapley(self) -> Dict[str, float]:
        k = len(self.block_names)
        shapley_values = {name: 0.0 for name in self.block_names}
        
        for name in self.block_names:
            other_names = [n for n in self.block_names if n != name]
            total_phi = 0.0
            
            for s_size in range(k):
                weight = (math_factorial(s_size) * math_factorial(k - s_size - 1)) / math_factorial(k)
                for subset in itertools.combinations(other_names, s_size):
                    v_without = self._evaluate_coalition(subset)
                    v_with = self._evaluate_coalition(subset + (name,))
                    total_phi += weight * (v_with - v_without)
                    
            shapley_values[name] = total_phi
            
        return shapley_values

    def audit_and_prune(self, threshold: float = 0.0) -> Dict[str, any]:
        shapley = self.compute_exact_shapley()
        retained = [name for name, phi in shapley.items() if phi > threshold]
        pruned = [name for name, phi in shapley.items() if phi <= threshold]
        
        base_score = self._evaluate_coalition(tuple())
        full_score = self._evaluate_coalition(tuple(self.block_names))
        pruned_score = self._evaluate_coalition(tuple(retained))
        
        return {
            "shapley_attributions": shapley,
            "retained_blocks": retained,
            "pruned_blocks": pruned,
            "baseline_score": base_score,
            "full_prompt_score": full_score,
            "pruned_prompt_score": pruned_score,
            "token_pruning_lift": pruned_score - full_score
        }

def math_factorial(n: int) -> int:
    import math
    return math.factorial(n)
```

---

## 3. Edge Cases & Failure Modes

1. **Syntax Interdependency Crash**: Ablating a preamble containing type declarations or XML tag definitions (`<instructions>`) can cause downstream blocks to generate unparseable formatting errors.
   - *Mitigation*: Structural DAG constraints enforcing that dependent blocks cannot be sampled without their parent schemas.
2. **Evaluation Metric Variance**: High output variance on small benchmark splits ($M < 30$) creates spurious Shapley values where random chance is attributed to prompt instructions.
   - *Mitigation*: Repeated trial evaluation with paired seed freezing across coalition comparisons.
