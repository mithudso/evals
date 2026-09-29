# Rabbithole Dossier: Attention Gradient Saliency Decontamination

## 1. Deep Mathematical Mechanics & Attribution Formulas

Let $\mathbf{x} = (x_1, \dots, x_N)$ be the token sequence of the evaluation prompt. Let $\mathbf{E} \in \mathbb{R}^{N \times d}$ be the embedding matrix of the prompt tokens. Let $F_k(\mathbf{E})$ be the logit for the ground truth target token at position $k$ of the expected agent output.

### Riemann Sum Approximation of Integrated Gradients

We approximate the path integral along the straight line from baseline embedding $\mathbf{E}'$ (all zeros or pad tokens) to $\mathbf{E}$ using $m$ interpolation steps:

$$\text{IG}_i(\mathbf{E}) \approx \frac{1}{m} \sum_{k=1}^m (\mathbf{E}_i - \mathbf{E}'_i) \odot \left. \nabla_{\mathbf{E}_i} F(\mathbf{E}' + \frac{k}{m}(\mathbf{E} - \mathbf{E}')) \right.$$

The scalar attribution score $A_i$ for prompt token $i$ across all output target tokens $T$ is:

$$A_i = \sum_{t=1}^T \|\text{IG}_i^{(t)}(\mathbf{E})\|_2$$

### Saliency Distribution and Leakage Anomaly Metric

Normalize the attributions to form a discrete probability distribution over prompt token indices $\{1, \dots, N\}$:

$$p_i = \frac{A_i}{\sum_{j=1}^N A_j}$$

Calculate prompt attention dispersion entropy $H(\mathbf{p})$:

$$H(\mathbf{p}) = - \sum_{i=1}^N p_i \ln(p_i + \epsilon)$$

Define the **Answer Leakage Score** $\mathcal{L}_{\text{leak}}$:

$$\mathcal{L}_{\text{leak}} = 1.0 - \frac{H(\mathbf{p})}{\ln(N)}$$

- If $\mathcal{L}_{\text{leak}} \ge 0.60$: Flag prompt as **Contaminated / Over-Specified**. A small cluster of prompt tokens is directly dictating the output without requiring agent reasoning.
- If $\mathcal{L}_{\text{leak}} \le 0.35$: Pass prompt as **Decontaminated / Healthy Task Context**.

---

## 2. Python Concrete Implementation Harness

```python
import math
from typing import List, Dict, Tuple

class SaliencyDecontaminator:
    def __init__(self, entropy_threshold: float = 0.50):
        self.entropy_threshold = entropy_threshold

    def calculate_leakage_metrics(self, token_attributions: List[float]) -> Dict[str, float]:
        """
        Given scalar attribution values per prompt token, computes entropy and leakage scores.
        """
        total = sum(token_attributions)
        if total <= 0:
            return {"leakage_score": 0.0, "entropy": 1.0, "is_contaminated": False}

        n = len(token_attributions)
        if n <= 1:
            return {"leakage_score": 1.0, "entropy": 0.0, "is_contaminated": True}

        # Normalize to probability distribution
        p = [a / total for a in token_attributions]
        
        # Shannon entropy
        h = -sum(prob * math.log(prob + 1e-12) for prob in p if prob > 0)
        max_h = math.log(n)
        
        # Leakage score (normalized concentration)
        leakage_score = 1.0 - (h / max_h)
        max_token_weight = max(p)
        
        return {
            "token_count": n,
            "entropy": h,
            "max_entropy": max_h,
            "leakage_score": leakage_score,
            "max_token_weight": max_token_weight,
            "is_contaminated": leakage_score >= self.entropy_threshold
        }

    def identify_giveaways(self, tokens: List[str], token_attributions: List[float], z_threshold: float = 2.5) -> List[Tuple[str, float]]:
        """
        Identifies outlier tokens with statistically anomalous attribution spikes.
        """
        if not token_attributions:
            return []
        
        mean_val = sum(token_attributions) / len(token_attributions)
        variance = sum((x - mean_val) ** 2 for x in token_attributions) / len(token_attributions)
        std_dev = math.sqrt(variance) if variance > 0 else 1e-6
        
        giveaways = []
        for token, attr in zip(tokens, token_attributions):
            z_score = (attr - mean_val) / std_dev
            if z_score >= z_threshold:
                giveaways.append((token, z_score))
                
        return sorted(giveaways, key=lambda x: x[1], reverse=True)
```

---

## 3. Edge Cases & Failure Modes

1. **Short Prompt Entropy Compression**: When a prompt consists of fewer than 10 tokens (e.g. `"Fix bug in auth.py"`), $N$ is small, which naturally compresses maximum entropy $\ln(N)$ and can trigger false positive leakage alerts.
   - *Mitigation*: Bypass entropy thresholding for prompts where $N < 15$; apply direct keyword collision tests instead.
2. **Gradient Saturation on Zero Baseline**: When interpolating from an all-zero embedding baseline, non-linear activation functions (e.g. SwiGLU) can experience zero gradient along early segments of the path.
   - *Mitigation*: Use Gauss-Legendre quadrature sampling with non-zero Gaussian noise baselines.
