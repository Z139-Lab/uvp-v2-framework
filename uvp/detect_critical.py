from __future__ import annotations

import pandas as pd


def detect_critical(scan_df: pd.DataFrame, band_half_width_points: int = 1) -> dict:
    if scan_df.empty:
        raise ValueError("scan_df is empty")

    idx = scan_df["critical_score"].idxmax()
    sigma_c = float(scan_df.loc[idx, "stress"])

    pos = scan_df.index.get_loc(idx)
    left = max(0, pos - band_half_width_points)
    right = min(len(scan_df) - 1, pos + band_half_width_points)

    critical_band = [float(scan_df.iloc[left]["stress"]), float(scan_df.iloc[right]["stress"])]

    support = {}
    for key in ["phi_var", "collapse_grad", "chi_mean"]:
        if key in scan_df.columns:
            support[key] = float(scan_df.loc[idx, key])

    return {
        "sigma_c": sigma_c,
        "critical_band": critical_band,
        "peak_score": float(scan_df.loc[idx, "critical_score"]),
        "method": "composite_scan",
        "confidence": "heuristic",
        "support": support,
    }
