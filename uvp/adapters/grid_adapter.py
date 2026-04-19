from __future__ import annotations

import pandas as pd


def _find_first(df: pd.DataFrame, candidates: list[str]) -> str | None:
    for c in candidates:
        if c in df.columns:
            return c
    return None


def adapt_grid(df: pd.DataFrame, columns: dict | None = None) -> pd.DataFrame:
    """Normalize multiple grid/UVP summary formats into canonical UVP schema."""
    columns = columns or {}
    out = pd.DataFrame(index=df.index)

    stress_col = columns.get("stress") or _find_first(df, ["stress", "sigma", "mw", "ai_p_mw"])
    L_col = columns.get("L") or _find_first(df, ["L", "size", "n_agents"])
    phi_col = columns.get("phi") or _find_first(df, ["phi", "phi_mean", "delta", "softening_collapse_rate"])
    collapse_col = columns.get("collapse_prob") or _find_first(df, ["collapse_prob", "baseline_collapse", "baseline_collapse_rate", "chi"])
    tau_col = columns.get("tau") or _find_first(df, ["tau", "mean_collapse_step"])
    seeds_col = columns.get("n_seeds") or _find_first(df, ["n_seeds", "n_runs", "runs"])

    if stress_col is None:
        raise ValueError(f"No stress-like column found. Present columns: {list(df.columns)}")
    out["stress"] = pd.to_numeric(df[stress_col], errors="coerce")

    if L_col is None:
        L_value = columns.get("default_L", 118)
        out["L"] = pd.Series([L_value] * len(df), index=df.index, dtype="float64")
    else:
        out["L"] = pd.to_numeric(df[L_col], errors="coerce")

    if phi_col is not None and phi_col in df.columns:
        out["phi"] = pd.to_numeric(df[phi_col], errors="coerce")
    elif "chi" in df.columns:
        out["phi"] = pd.to_numeric(df["chi"], errors="coerce")
    else:
        raise ValueError("No phi-like column found (phi, phi_mean, delta, softening_collapse_rate)")

    if collapse_col is not None and collapse_col in df.columns:
        out["collapse_prob"] = pd.to_numeric(df[collapse_col], errors="coerce")
    else:
        if "chi" in df.columns:
            chi = pd.to_numeric(df["chi"], errors="coerce")
            denom = chi.max() if pd.notna(chi.max()) and chi.max() != 0 else 1.0
            out["collapse_prob"] = chi / denom
        else:
            out["collapse_prob"] = 1.0 - out["phi"].clip(lower=0, upper=1)

    if tau_col is not None and tau_col in df.columns:
        out["tau"] = pd.to_numeric(df[tau_col], errors="coerce")
    else:
        out["tau"] = pd.NA

    if seeds_col is not None and seeds_col in df.columns:
        out["n_seeds"] = pd.to_numeric(df[seeds_col], errors="coerce")
    else:
        out["n_seeds"] = pd.NA

    for col in ["chi", "phi_var", "cv", "variant", "experiment", "topology", "regime", "nonconv_prob"]:
        if col in df.columns:
            out[col] = df[col]

    out["source"] = "grid"
    return out.dropna(subset=["stress", "L", "phi"]).reset_index(drop=True)
