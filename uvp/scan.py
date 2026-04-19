from __future__ import annotations

import numpy as np
import pandas as pd

from .metrics import zscore


def compute_scan(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate by stress and build a practical criticality scan."""
    agg_map = {
        "phi_mean": ("phi", "mean"),
        "phi_std": ("phi", "std"),
        "n_L": ("L", "nunique"),
    }
    if "collapse_prob" in df.columns:
        agg_map["collapse_mean"] = ("collapse_prob", "mean")
        agg_map["collapse_std"] = ("collapse_prob", "std")
    if "chi" in df.columns:
        agg_map["chi_mean"] = ("chi", "mean")
    if "phi_var" in df.columns:
        agg_map["phi_var_mean"] = ("phi_var", "mean")

    base = (
        df.groupby("stress", as_index=False)
        .agg(**agg_map)
        .sort_values("stress")
        .reset_index(drop=True)
    )

    base["phi_var"] = base.get("phi_var_mean", base["phi_std"].fillna(0.0) ** 2)

    if "collapse_mean" in base.columns and len(base) >= 3:
        grad = np.gradient(base["collapse_mean"].to_numpy(dtype=float), base["stress"].to_numpy(dtype=float))
        base["collapse_grad"] = np.abs(grad)
    else:
        base["collapse_grad"] = 0.0

    chi_term = zscore(base["chi_mean"].to_numpy()) if "chi_mean" in base.columns else 0.0
    phi_var_term = zscore(base["phi_var"].to_numpy())
    grad_term = zscore(base["collapse_grad"].to_numpy()) if "collapse_grad" in base.columns else 0.0

    base["critical_score"] = 0.5 * np.asarray(phi_var_term) + 0.3 * np.asarray(grad_term) + 0.2 * np.asarray(chi_term)
    return base
