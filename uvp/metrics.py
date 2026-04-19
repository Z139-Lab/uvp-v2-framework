from __future__ import annotations

import numpy as np
import pandas as pd


def zscore(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    sd = np.nanstd(x)
    if sd == 0 or np.isnan(sd):
        return np.zeros_like(x)
    return (x - np.nanmean(x)) / sd


def collapse_alignment_error(df: pd.DataFrame, x_col: str = "x_scaled", y_col: str = "y_scaled") -> float:
    """Simple heuristic: compare linearly interpolated curves over shared x-range."""
    groups = list(df.groupby("L"))
    if len(groups) < 2:
        return float("inf")

    x_mins = []
    x_maxs = []
    cleaned = []
    for L, g in groups:
        g = g[[x_col, y_col]].dropna().sort_values(x_col)
        if len(g) < 3:
            continue
        x = g[x_col].to_numpy(dtype=float)
        y = g[y_col].to_numpy(dtype=float)
        if np.any(np.diff(x) == 0):
            _, uniq_idx = np.unique(x, return_index=True)
            x = x[uniq_idx]
            y = y[uniq_idx]
        if len(x) < 3:
            continue
        cleaned.append((L, x, y))
        x_mins.append(x.min())
        x_maxs.append(x.max())

    if len(cleaned) < 2:
        return float("inf")

    lo = max(x_mins)
    hi = min(x_maxs)
    if not np.isfinite(lo) or not np.isfinite(hi) or hi <= lo:
        return float("inf")

    grid = np.linspace(lo, hi, 100)
    curves = []
    for _, x, y in cleaned:
        curves.append(np.interp(grid, x, y))
    arr = np.vstack(curves)
    mean_curve = np.nanmean(arr, axis=0)
    return float(np.nanmean((arr - mean_curve) ** 2))
