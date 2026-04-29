import numpy as np


# =========================
# ACTIVATION
# =========================
def activation_logistic(x, k=8.0, threshold=0.72):
    return 1.0 / (1.0 + np.exp(-k * (x - threshold)))


# =========================
# MEMORY
# =========================
def memory_exponential(current, memory, alpha=0.2):
    return alpha * current + (1 - alpha) * memory


# =========================
# NOISE
# =========================
def noise_gaussian(rng, scale=0.08):
    return rng.normal(0.0, scale)


# =========================
# ENGINE
# =========================
class MicroRuleEngine:

    def __init__(self, activation_name="logistic", memory_name="exponential", noise_name="gaussian", seed=42):
        self.rng = np.random.default_rng(seed)

    def update_memory(self, current, memory):
        return memory_exponential(current, memory)

    def failure_prob(self, accumulated):
        noise = noise_gaussian(self.rng)
        x = np.clip(accumulated + noise, 0.0, 1.0)

        base_p = activation_logistic(x)

        # 🔥 控制強度（關鍵）
        p = 0.35 * base_p

        return np.clip(p, 0.0, 1.0)