from __future__ import annotations

import pandas as pd


def adapt_llm(df: pd.DataFrame, columns: dict | None = None) -> pd.DataFrame:
    columns = columns or {}

    aliases = {
        columns.get("stress", "stress"): "stress",
        columns.get("L", "L"): "L",
        columns.get("collapse_prob", "collapse_prob"): "collapse_prob",
        columns.get("phi", "phi"): "phi",
    }

    tau_col = columns.get("tau", "tau")
    if tau_col in df.columns:
        aliases[tau_col] = "tau"

    n_col = columns.get("n_seeds", "n_seeds")
    if n_col in df.columns:
        aliases[n_col] = "n_seeds"

    out = df.rename(columns=aliases).copy()

    # Common LLM extras are preserved if present.
    for extra in ["topology", "memory", "variant", "system"]:
        if extra in df.columns and extra not in out.columns:
            out[extra] = df[extra]

    for col in ["stress", "L", "collapse_prob", "phi"]:
        out[col] = pd.to_numeric(out[col], errors="coerce")
    if "tau" in out.columns:
        out["tau"] = pd.to_numeric(out["tau"], errors="coerce")
    if "n_seeds" in out.columns:
        out["n_seeds"] = pd.to_numeric(out["n_seeds"], errors="coerce")
    out["source"] = out.get("source", "llm")
    return out
