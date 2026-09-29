# Rabbithole Dossier: Wald SPRT Log-Odds Martingale Gating

## 1. Deep Mathematical Mechanics & Closed-Form Integer Grid

Let the two competing hypotheses for challenger pass rate $p$ be:
- $H_0: p = p_0$ (Baseline champion performance)
- $H_1: p = p_1$ (Challenger acceptable target, with $p_1 > p_0$)

Given error parameters $\alpha \in (0, 1)$ and $\beta \in (0, 1)$, compute boundary log-constants:

$$A = \ln \left( \frac{1 - \beta}{\alpha} \right), \quad B = \ln \left( \frac{\beta}{1 - \alpha} \right)$$

Log-likelihood ratios per success and failure:

$$u = \ln\left(\frac{p_1}{p_0}\right) > 0, \quad v = \ln\left(\frac{1 - p_1}{1 - p_0}\right) < 0$$

Define denominator constant $D = u - v = \ln\left(\frac{p_1 (1 - p_0)}{p_0 (1 - p_1)}\right) > 0$.

The boundary slope $s$ and intercepts $h_0, h_1$ in the $(m, S_m)$ plane are:

$$s = \frac{-v}{D} = \frac{\ln\left(\frac{1 - p_0}{1 - p_1}\right)}{\ln\left(\frac{p_1 (1 - p_0)}{p_0 (1 - p_1)}\right)}$$

$$h_0 = \frac{B}{D}, \quad h_1 = \frac{A}{D}$$

### Decision State Logic
For trial $m \in \{1, 2, \dots, M_{\max}\}$ and successes $S_m \in \{0, \dots, m\}$:
- **Accept $H_1$ (Promote Candidate)** if: $S_m \ge \lceil s \cdot m + h_1 \rceil$
- **Reject $H_1$ (Abort Deployment)** if: $S_m \le \lfloor s \cdot m + h_0 \rfloor$
- **Continue Testing** if: $\lfloor s \cdot m + h_0 \rfloor < S_m < \lceil s \cdot m + h_1 \rceil$

---

## 2. Python Concrete Implementation Harness

```python
import math
from typing import Dict, List, Tuple

class MartingaleSPRTGater:
    def __init__(self, p0: float = 0.85, p1: float = 0.95, alpha: float = 0.01, beta: float = 0.05, max_m: int = 150):
        self.p0 = p0
        self.p1 = p1
        self.alpha = alpha
        self.beta = beta
        self.max_m = max_m
        
        # Log-odds constants
        u = math.log(p1 / p0)
        v = math.log((1.0 - p1) / (1.0 - p0))
        D = u - v
        
        self.s = -v / D
        self.h0 = math.log(beta / (1.0 - alpha)) / D
        self.h1 = math.log((1.0 - beta) / alpha) / D
        
        # Precompute integer boundary grid
        self.upper_bounds = []
        self.lower_bounds = []
        for m in range(max_m + 1):
            if m == 0:
                self.upper_bounds.append(None)
                self.lower_bounds.append(None)
            else:
                self.upper_bounds.append(math.ceil(self.s * m + self.h1))
                self.lower_bounds.append(math.floor(self.s * m + self.h0))

    def evaluate_step(self, m: int, successes: int) -> str:
        """
        O(1) decision lookup against precomputed grid.
        Returns: 'PROMOTE', 'ABORT', or 'CONTINUE'
        """
        if m > self.max_m:
            return "PROMOTE" if (successes / m) >= self.p0 else "ABORT"
            
        up = self.upper_bounds[m]
        low = self.lower_bounds[m]
        
        if successes >= up:
            return "PROMOTE"
        elif successes <= low:
            return "ABORT"
        else:
            return "CONTINUE"
```

---

## 3. Edge Cases & Failure Modes

1. **Unreachable Early Acceptance**: For early trials (e.g. $m \le 5$), the acceptance boundary $s \cdot m + h_1 > m$, making it mathematically impossible to accept immediately because successes cannot exceed trials.
   - *Behavior*: Correctly enforced by mathematics; ensures minimum sample size is observed before certification.
2. **Deterministic Golden Invariant Failures**: If candidate regresses on an absolute critical test (e.g. security bypass), waiting for SPRT lower bound wastes steps.
   - *Mitigation*: Hard circuit breaker: any failure in $\mathcal{G}_{\text{golden}}$ overrides SPRT and aborts at $m$.
