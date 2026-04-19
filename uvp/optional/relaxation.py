from __future__ import annotations

import pandas as pd


def fit_relaxation_summary(df: pd.DataFrame) -> pd.DataFrame:
    if "tau" not in df.columns:
        raise ValueError("tau column not found")
    out = (
        df.dropna(subset=["tau"])
        .groupby(["stress", "L"], as_index=False)
        .agg(tau_mean=("tau", "mean"), tau_std=("tau", "std"), n=("tau", "count"))
        .sort_values(["stress", "L"])
    )
    return out
