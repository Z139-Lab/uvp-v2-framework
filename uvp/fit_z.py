from __future__ import annotations

import numpy as np
import pandas as pd

from .collapse import prepare_collapse
from .metrics import collapse_alignment_error


def _nearest_stress_slice(df: pd.DataFrame, sigma_c: float, frac: float = 0.15) -> pd.DataFrame:
    stresses = np.sort(df["stress"].dropna().unique())
    if len(stresses) == 0:
        return df.iloc[0:0].copy()
    if len(stresses) == 1:
        return df[df["stress"] == stresses[0]].copy()
    span = stresses.max() - stresses.min()
    diffs = np.diff(stresses)
    min_step = np.min(diffs[diffs > 0]) if np.any(diffs > 0) else 0.0
    tol = max(span * frac, min_step + 1e-12)
    return df[np.abs(df["stress"] - sigma_c) <= tol].copy()


def fit_z_from_tau(df: pd.DataFrame, sigma_c: float, stress_window_fraction: float = 0.15) -> dict:
    if "tau" not in df.columns or df["tau"].dropna().empty:
        raise ValueError("tau column missing or empty")

    window = _nearest_stress_slice(df.dropna(subset=["tau"]), sigma_c, stress_window_fraction)
    by_L = window.groupby("L", as_index=False).agg(tau_mean=("tau", "mean"))
    by_L = by_L[(by_L["L"] > 0) & (by_L["tau_mean"] > 0)]
    if len(by_L) < 2:
        raise ValueError("Not enough (L, tau) points near sigma_c for z fit")

    x = np.log(by_L["L"].to_numpy(dtype=float))
    y = np.log(by_L["tau_mean"].to_numpy(dtype=float))
    z, intercept = np.polyfit(x, y, 1)
    yhat = z * x + intercept
    resid = y - yhat
    err = float(np.sqrt(np.mean(resid ** 2)))

    return {
        "method": "tau_power_law",
        "z_best": float(z),
        "z_min": float(z - err),
        "z_max": float(z + err),
        "fit_rmse_log": err,
        "n_points": int(len(by_L)),
    }


def fit_z_by_scan(df: pd.DataFrame, sigma_c: float, z_min: float = 0.5, z_max: float = 2.5, z_steps: int = 101) -> dict:
    if df["L"].nunique() < 2:
        return {
            "method": "insufficient_multi_L",
            "z_best": None,
            "z_min": None,
            "z_max": None,
            "error_min": None,
            "message": "Need at least two system sizes (L) for collapse-based z scan.",
        }

    zs = np.linspace(z_min, z_max, z_steps)
    errors = []
    for z in zs:
        cdf = prepare_collapse(df, sigma_c=sigma_c, z=float(z))
        errors.append(collapse_alignment_error(cdf))

    errors = np.asarray(errors, dtype=float)
    if np.all(~np.isfinite(errors)):
        return {
            "method": "collapse_proxy_scan_failed",
            "z_best": None,
            "z_min": None,
            "z_max": None,
            "error_min": None,
            "message": "Collapse proxy scan produced no finite alignment error.",
        }

    best_idx = int(np.nanargmin(errors))
    best_z = float(zs[best_idx])
    min_err = float(errors[best_idx])
    tol = min_err * 1.10 if np.isfinite(min_err) else np.inf
    valid = np.where(errors <= tol)[0]
    z_lo = float(zs[valid[0]]) if len(valid) else best_z
    z_hi = float(zs[valid[-1]]) if len(valid) else best_z

    return {
        "method": "collapse_proxy_scan",
        "z_best": best_z,
        "z_min": z_lo,
        "z_max": z_hi,
        "error_min": min_err,
        "z_grid": zs.tolist(),
        "error_grid": errors.tolist(),
    }


def fit_z_auto(df: pd.DataFrame, sigma_c: float, cfg: dict | None = None) -> dict:
    cfg = cfg or {}
    try:
        return fit_z_from_tau(df, sigma_c=sigma_c, stress_window_fraction=float(cfg.get("stress_window_fraction", 0.15)))
    except Exception:
        return fit_z_by_scan(df, sigma_c=sigma_c, z_min=float(cfg.get("z_min", 0.5)), z_max=float(cfg.get("z_max", 2.5)), z_steps=int(cfg.get("z_steps", 101)))
