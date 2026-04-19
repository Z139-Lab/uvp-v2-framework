from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def plot_scan(scan_df: pd.DataFrame, sigma_c: float, output_path: str | Path) -> None:
    plt.figure(figsize=(7, 4.5))
    plt.plot(scan_df["stress"], scan_df["critical_score"], marker="o")
    plt.axvline(sigma_c, linestyle="--")
    plt.xlabel("stress")
    plt.ylabel("critical score")
    plt.title("UVP scan")
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()


def plot_collapse(collapse_df: pd.DataFrame, output_path: str | Path) -> None:
    plt.figure(figsize=(7, 4.5))
    for L, g in collapse_df.groupby("L"):
        plt.plot(g["x_scaled"], g["y_scaled"], marker="o", linestyle="-", label=f"L={L}")
    plt.xlabel("x_scaled")
    plt.ylabel("y_scaled")
    plt.title("Collapse view")
    plt.legend(fontsize=8)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()


def plot_z_curve(z_result: dict, output_path: str | Path) -> None:
    if z_result.get("method") != "collapse_proxy_scan":
        return
    plt.figure(figsize=(7, 4.5))
    plt.plot(z_result["z_grid"], z_result["error_grid"], marker="o", linestyle="-")
    plt.xlabel("z")
    plt.ylabel("collapse error")
    plt.title("z scan")
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()
