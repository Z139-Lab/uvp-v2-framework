from __future__ import annotations

import pandas as pd


def prepare_collapse(df: pd.DataFrame, sigma_c: float, z: float | None = None) -> pd.DataFrame:
    out = df.copy()
    # Placeholder reduced variable. A fuller version may add nu-like scaling later.
    out["x_scaled"] = (out["stress"] - sigma_c) * out["L"]

    if z is None:
        out["y_scaled"] = out["phi"]
    else:
        out["y_scaled"] = out["phi"] * (out["L"] ** z)
    return out
