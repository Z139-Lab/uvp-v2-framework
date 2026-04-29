import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# =========================
# 讀取資料
# =========================
path = r"micro_rule\micro_rule_summary_results.csv"
df = pd.read_csv(path)

print("Rows:", len(df))
print("Columns:", list(df.columns))

# =========================
# 強制轉型
# =========================
for col in ["stress", "chi", "L"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.dropna(subset=["stress", "chi", "L"]).copy()

print("After clean:", len(df))
print(df[["stress", "chi", "L"]].head())

if len(df) == 0:
    raise ValueError("清洗後沒有資料 → CSV 格式有問題")

# =========================
# 平均化
# =========================
grouped = (
    df.groupby(["L", "stress"], as_index=False)
      .agg(
          chi_mean=("chi", "mean"),
          chi_std=("chi", "std"),
          n=("chi", "size")
      )
)

grouped["chi_std"] = grouped["chi_std"].fillna(0.0)
grouped["chi_sem"] = grouped["chi_std"] / np.sqrt(grouped["n"].clip(lower=1))

print("\nGrouped preview:")
print(grouped.head())

# =========================
# Figure 2A clean
# =========================
plt.figure(figsize=(8, 6))

for L in sorted(grouped["L"].unique()):
    sub = grouped[grouped["L"] == L].sort_values("stress")
    plt.plot(
        sub["stress"],
        sub["chi_mean"],
        marker="o",
        linewidth=2,
        label=f"L={int(L)}"
    )

plt.xlabel("Stress")
plt.ylabel("Chi = L * Var(phi)")
plt.title("Figure 2A: Susceptibility vs Stress")
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("figure2A_chi_vs_stress_clean.png", dpi=200)
plt.show()

# =========================
# Figure 2A diagnostic with error bars
# =========================
plt.figure(figsize=(8, 6))

for L in sorted(grouped["L"].unique()):
    sub = grouped[grouped["L"] == L].sort_values("stress")

    plt.errorbar(
        sub["stress"],
        sub["chi_mean"],
        yerr=sub["chi_sem"],   # 用標準誤，比 std 更適合診斷平均值穩定性
        marker="o",
        linewidth=1.8,
        capsize=4,
        label=f"L={int(L)}"
    )

plt.xlabel("Stress")
plt.ylabel("Chi = L * Var(phi)")
plt.title("Figure 2A (diagnostic): Susceptibility vs Stress with SEM")
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("figure2A_chi_vs_stress_errorbar.png", dpi=200)
plt.show()

# =========================
# Figure 2B peak scaling
# =========================
peaks = []

for L in sorted(grouped["L"].unique()):
    sub = grouped[grouped["L"] == L].sort_values("stress")
    idx = sub["chi_mean"].idxmax()
    peaks.append({
        "L": sub.loc[idx, "L"],
        "stress_peak": sub.loc[idx, "stress"],
        "chi_max": sub.loc[idx, "chi_mean"]
    })

peaks = pd.DataFrame(peaks)

print("\nPeaks:")
print(peaks)

plt.figure(figsize=(7, 6))
plt.loglog(peaks["L"], peaks["chi_max"], "o-", linewidth=2)
plt.xlabel("L")
plt.ylabel("Chi_max")
plt.title("Figure 2B: Peak Scaling")
plt.grid(True, which="both", alpha=0.3)
plt.tight_layout()
plt.savefig("figure2B_peak_scaling_clean.png", dpi=200)
plt.show()