# Rabbithole Dossier: Bayesian Sequential Canary Early Stopping

## 1. Deep Mathematical Mechanics & SPRT Equations

Let $p_0$ denote the null hypothesis probability (incumbent champion baseline), and $p_1$ denote the alternative hypothesis (target challenger bar, $p_1 > p_0$).

Define parameters:
- $\alpha$: Permitted Type I error rate (e.g., $\alpha = 0.01$)
- $\beta$: Permitted Type II error rate (e.g., $\beta = 0.05$)

Decision thresholds:

$$A = \ln\left( \frac{1 - \beta}{\alpha} \right) \quad (\text{Promote/Accept})$$
$$B = \ln\left( \frac{\beta}{1 - \alpha} \right) \quad (\text{Abort/Reject})$$

Let $m$ be the number of executed test cases, and $S_m = \sum_{i=1}^m X_i$ be the number of passed tests ($X_i \in \{0, 1\}$).

The cumulative log-likelihood ratio $\Lambda_m$ is:

$$\Lambda_m = S_m \cdot k_1 + (m - S_m) \cdot k_0$$

Where constants $k_1$ and $k_0$ are:

$$k_1 = \ln\left( \frac{p_1}{p_0} \right), \quad k_0 = \ln\left( \frac{1 - p_1}{1 - p_0} \right)$$

### Decision Boundary Lines in $(m, S_m)$ Space

We express the stopping rules as linear boundaries on the number of successes $S_m$:

$$\text{Upper Line } (Accept): \quad S_m \ge \frac{A - m \cdot k_0}{k_1 - k_0} = s \cdot m + h_1$$
$$\text{Lower Line } (Reject): \quad S_m \le \frac{B - m \cdot k_0}{k_1 - k_0} = s \cdot m + h_0$$

Where slope $s$ and intercepts $h_0, h_1$ are:

$$s = \frac{\ln\left( \frac{1 - p_0}{1 - p_1} \right)}{\ln\left( \frac{p_1}{p_0} \right) + \ln\left( \frac{1 - p_0}{1 - p_1} \right)}$$

$$h_0 = \frac{B}{\ln\left( \frac{p_1}{p_0} \right) - \ln\left( \frac{1 - p_1}{1 - p_0} \right)}, \quad h_1 = \frac{A}{\ln\left( \frac{p_1}{p_0} \right) - \ln\left( \frac{1 - p_1}{1 - p_0} \right)}$$

---

## 2. Python Concrete Implementation Harness

```python
import math
from typing import Literal, Tuple, Optional

class SequentialCanaryGater:
    def __init__(
        self,
        p0: float = 0.85,  # Incumbent baseline pass rate
        p1: float = 0.95,  # Challenger target pass rate
        alpha: float = 0.01,  # Max false promotion rate
        beta: float = 0.05,   # Max false rejection rate
        max_horizon: int = 200
    ):
        assert 0.0 < p0 < p1 < 1.0
        self.p0 = p0
        self.p1 = p1
        self.alpha = alpha
        self.beta = beta
        self.max_horizon = max_horizon
        
        # Log thresholds
        self.A = math.log((1.0 - beta) / alpha)
        self.B = math.log(beta / (1.0 - alpha))
        
        # Incremental log-likelihood constants
        self.k1 = math.log(p1 / p0)
        self.k0 = math.log((1.0 - p1) / (1.0 - p0))
        
        # State
        self.m = 0
        self.successes = 0
        self.log_likelihood_ratio = 0.0
        self.status: Literal["CONTINUE", "PROMOTE", "ABORT"] = "CONTINUE"

    def record_result(self, passed: bool) -> Literal["CONTINUE", "PROMOTE", "ABORT"]:
        if self.status != "CONTINUE":
            return self.status

        self.m += 1
        if passed:
            self.successes += 1
            self.log_likelihood_ratio += self.k1
        else:
            self.log_likelihood_ratio += self.k0

        if self.log_likelihood_ratio >= self.A:
            self.status = "PROMOTE"
        elif self.log_likelihood_ratio <= self.B:
            self.status = "ABORT"
        elif self.m >= self.max_horizon:
            # Truncated SPRT resolution
            self.status = "PROMOTE" if self.successes / self.m >= self.p0 else "ABORT"

        return self.status

    def get_summary(self) -> dict:
        return {
            "evaluations_run": self.m,
            "success_count": self.successes,
            "empirical_pass_rate": (self.successes / self.m) if self.m > 0 else 0.0,
            "log_likelihood_ratio": self.log_likelihood_ratio,
            "threshold_A": self.A,
            "threshold_B": self.B,
            "decision": self.status,
            "compute_saved_pct": max(0.0, (1.0 - (self.m / self.max_horizon)) * 100.0)
        }
```

---

## 3. Edge Cases & Failure Modes

1. **Undetected Flake Burst**: A temporary downstream API glitch fails 3 consecutive requests on a candidate that is fundamentally sound, causing immediate unwarranted abortion ($S_m \le B$).
   - *Mitigation*: Flake-retry policy: any network/timeout error prompts a deterministic secondary retry before recording $X_i = 0$.
2. **Truncation Drift (Horizon Limit Exhaustion)**: When a candidate's true performance is exactly $(p_0 + p_1) / 2$, $\Lambda_m$ drifts horizontally inside $(B, A)$ indefinitely.
   - *Mitigation*: Hard horizon cap $M_{\max} = 200$, resolving via empirical threshold $p_{\text{emp}} \ge p_0$.
