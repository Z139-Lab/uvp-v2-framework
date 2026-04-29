"""
analyze_uvp_results.py
======================
Analysis engine for UVP-01.

Reads summary_results.csv (from run_uvp_experiments.py) and produces:
  - fit_table.csv        (z exponent fits per variant)
  - collapse_metrics.csv (cross-L CV per variant)
  - uvp_final_report.txt (human-readable classification + level assignment)

Usage:
  python analyze_uvp_results.py                          # uses uvp_config.yaml
  python analyze_uvp_results.py --config my.yaml
  python analyze_uvp_results.py --input custom_data.csv
"""

import argparse
import csv
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import yaml
from scipy import stats

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s  %(levelname)s  %(message)s",
                    datefmt="%H:%M:%S")
log = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# FSS CORE: z EXPONENT FITTING
# ─────────────────────────────────────────────

def find_peak_chi(df_variant: pd.DataFrame, L: int) -> Tuple[float, float]:
    """
    Returns (peak_stress, chi_at_peak) for a given L in one variant's data.
    Uses smoothed peak detection.
    """
    sub = df_variant[df_variant["L"] == L].sort_values("stress")
    if sub.empty:
        return np.nan, np.nan

    chi_vals = sub["chi"].values
    stress_vals = sub["stress"].values

    # Smooth slightly to reduce noise effects
    if len(chi_vals) > 3:
        kernel = np.array([0.25, 0.50, 0.25])
        smoothed = np.convolve(chi_vals, kernel, mode="same")
        smoothed[0]  = chi_vals[0]
        smoothed[-1] = chi_vals[-1]
    else:
        smoothed = chi_vals

    peak_idx = np.argmax(smoothed)
    return float(stress_vals[peak_idx]), float(chi_vals[peak_idx])


def fit_z_exponent(
    L_values: List[int],
    chi_peaks: List[float],
    min_points: int = 3,
) -> Dict[str, Any]:
    """
    Fits χ_max ~ L^z via OLS in log-log space.
    Returns dict with z, r2, stderr, n_points, fit_valid.
    """
    valid = [(L, chi) for L, chi in zip(L_values, chi_peaks)
             if chi > 0 and np.isfinite(chi) and L > 0]

    if len(valid) < min_points:
        return {
            "z": np.nan, "r2": np.nan, "z_stderr": np.nan,
            "n_points": len(valid), "fit_valid": False,
            "log_L": [], "log_chi": [],
        }

    log_L   = np.log(np.array([v[0] for v in valid], dtype=float))
    log_chi = np.log(np.array([v[1] for v in valid], dtype=float))

    slope, intercept, r_value, p_value, stderr = stats.linregress(log_L, log_chi)

    return {
        "z":         float(slope),
        "z_intercept": float(intercept),
        "r2":        float(r_value ** 2),
        "z_stderr":  float(stderr),
        "p_value":   float(p_value),
        "n_points":  len(valid),
        "fit_valid": True,
        "log_L":     log_L.tolist(),
        "log_chi":   log_chi.tolist(),
    }


# ─────────────────────────────────────────────
# COLLAPSE METRIC
# ─────────────────────────────────────────────

def compute_collapse_cv(
    df_variant: pd.DataFrame,
    z: float,
    stress_window: Tuple[float, float] = (0.88, 0.92),
) -> Dict[str, float]:
    """
    Computes Cross-L CV of scaled susceptibility χ / L^z.

    For each stress point, compute CV across different L values.
    Returns mean and max CV, plus overall collapse_cv.
    """
    df_w = df_variant[
        (df_variant["stress"] >= stress_window[0]) &
        (df_variant["stress"] <= stress_window[1])
    ].copy()

    if df_w.empty or np.isnan(z):
        return {"collapse_cv": np.nan, "mean_cv": np.nan, "max_cv": np.nan,
                "n_stress_points": 0}

    df_w["scaled_chi"] = df_w["chi"] / (df_w["L"] ** z)

    cvs = []
    for stress_val, grp in df_w.groupby("stress"):
        if len(grp) < 2:
            continue
        mean_s = grp["scaled_chi"].mean()
        std_s  = grp["scaled_chi"].std()
        if mean_s > 1e-12:
            cvs.append(std_s / mean_s)

    if not cvs:
        return {"collapse_cv": np.nan, "mean_cv": np.nan, "max_cv": np.nan,
                "n_stress_points": 0}

    return {
        "collapse_cv":    float(np.mean(cvs)),
        "mean_cv":        float(np.mean(cvs)),
        "max_cv":         float(np.max(cvs)),
        "n_stress_points": len(cvs),
    }


# ─────────────────────────────────────────────
# CLASSIFICATION
# ─────────────────────────────────────────────

def classify_variant(
    z: float,
    r2: float,
    peak_stress: float,
    collapse_cv: float,
    z_ref: float,
    thresholds: Dict,
) -> Tuple[str, str]:
    """
    Returns (classification, reason).
    Classification: PASS | CONDITIONAL_PASS | FAIL
    """
    if np.isnan(z) or np.isnan(r2):
        return "FAIL", "insufficient data for fit"

    delta_z    = abs(z - z_ref)
    peak_drift = abs(peak_stress - 0.9) if not np.isnan(peak_stress) else 999

    pass_c = thresholds["pass_conditions"]
    cond_c = thresholds["conditional_pass_conditions"]

    if (delta_z    <= pass_c["max_delta_z"]  and
        r2         >= pass_c["min_r2"]        and
        peak_drift <= pass_c["max_peak_drift"]):
        return "PASS", f"Δz={delta_z:.3f} R²={r2:.3f} peak_drift={peak_drift:.3f}"

    if (delta_z    <= cond_c["max_delta_z"]  and
        r2         >= cond_c["min_r2"]        and
        peak_drift <= cond_c["max_peak_drift"]):
        return "CONDITIONAL_PASS", (
            f"Δz={delta_z:.3f} (loose) R²={r2:.3f} peak_drift={peak_drift:.3f}")

    reasons = []
    if delta_z    > cond_c["max_delta_z"]:  reasons.append(f"Δz={delta_z:.3f} too large")
    if r2         < cond_c["min_r2"]:       reasons.append(f"R²={r2:.3f} too low")
    if peak_drift > cond_c["max_peak_drift"]: reasons.append(f"peak_drift={peak_drift:.3f}")
    return "FAIL", "; ".join(reasons)


def assign_level(fit_rows: List[Dict], collapse_rows: List[Dict],
                 level_cfg: Dict) -> Tuple[int, str]:
    """
    Assigns universality level 1 / 2 / 3 based on aggregate pass rates.
    Returns (level, description).
    """
    micro_rows = [r for r in fit_rows if r.get("experiment") == "micro_rule"]
    topo_rows  = [r for r in fit_rows if r.get("experiment") == "topology"]

    def pass_rate(rows):
        if not rows:
            return 0.0
        n_pass = sum(1 for r in rows
                     if r["classification"] in ("PASS", "CONDITIONAL_PASS"))
        return n_pass / len(rows)

    micro_pr = pass_rate(micro_rows)
    topo_pr  = pass_rate(topo_rows)

    avg_cv = np.nanmean([r.get("collapse_cv", np.nan) for r in collapse_rows]) \
             if collapse_rows else np.nan
    all_dz = [abs(r.get("z", np.nan) - r.get("z_ref", 1.387))
              for r in fit_rows if r.get("fit_valid")]
    max_dz = float(np.nanmax(all_dz)) if all_dz else np.nan

    def _req(level_key, field):
        """Extract scalar from required list-of-dicts or dict."""
        req = level_cfg[level_key]["required"]
        if isinstance(req, dict):
            return req.get(field)
        # YAML list of single-key dicts: [{key: val}, ...]
        for item in req:
            if isinstance(item, dict) and field in item:
                return item[field]
        return None

    # Check Level 3
    l3_micro = _req("level_3", "micro_rule_pass_rate")
    l3_topo  = _req("level_3", "topology_pass_rate")
    l3_cv    = _req("level_3", "collapse_cv_max")
    l3_dz    = _req("level_3", "delta_z_all_variants_max")
    if (l3_micro and micro_pr >= l3_micro and
        l3_topo  and topo_pr  >= l3_topo  and
        l3_cv    and not np.isnan(avg_cv) and avg_cv <= l3_cv and
        l3_dz    and not np.isnan(max_dz) and max_dz <= l3_dz):
        return 3, level_cfg["level_3"]["description"]

    # Check Level 2
    l2_micro = _req("level_2", "micro_rule_pass_rate")
    l2_topo  = _req("level_2", "topology_pass_rate")
    l2_cv    = _req("level_2", "collapse_cv_max")
    if (l2_micro and micro_pr >= l2_micro and
        l2_topo  and topo_pr  >= l2_topo  and
        (l2_cv is None or np.isnan(avg_cv) or avg_cv <= l2_cv)):
        return 2, level_cfg["level_2"]["description"]

    # Check Level 1
    l1_micro = _req("level_1", "micro_rule_pass_rate")
    l1_topo  = _req("level_1", "topology_pass_rate")
    if (l1_micro and micro_pr >= l1_micro and
        l1_topo  and topo_pr  >= l1_topo):
        return 1, level_cfg["level_1"]["description"]

    return 0, "Below Level 1 — scaling not yet established across variants"


# ─────────────────────────────────────────────
# MAIN ANALYSIS PIPELINE
# ─────────────────────────────────────────────

def analyze(cfg: Dict, input_csv: Path, output_dir: Path):
    fss_cfg   = cfg["fss_analysis"]
    class_cfg = cfg["classification"]
    z_ref     = fss_cfg["z_reference"]

    log.info(f"Loading data from {input_csv}")
    df = pd.read_csv(input_csv)
    log.info(f"  Rows: {len(df)}  Variants: {df['variant'].nunique()}  "
             f"Experiments: {df['experiment'].nunique()}")

    fit_rows      = []
    collapse_rows = []

    experiments = df["experiment"].unique()
    for exp_name in experiments:
        df_exp = df[df["experiment"] == exp_name]
        variants = df_exp["variant"].unique()
        log.info(f"Processing experiment '{exp_name}': {len(variants)} variants")

        for variant in variants:
            df_var = df_exp[df_exp["variant"] == variant]
            L_values = sorted(df_var["L"].unique())

            # Find chi peaks per L
            chi_peaks   = []
            peak_stresses = []
            for L in L_values:
                ps, chi_p = find_peak_chi(df_var, L)
                chi_peaks.append(chi_p)
                peak_stresses.append(ps)

            peak_stress_mean = float(np.nanmean(peak_stresses))

            # Fit z
            fit = fit_z_exponent(L_values, chi_peaks,
                                  min_points=fss_cfg["min_sizes_for_fit"])

            # Collapse CV
            z_use = fit["z"] if fit["fit_valid"] else z_ref
            coll  = compute_collapse_cv(
                df_var, z=z_use,
                stress_window=tuple(fss_cfg["collapse_window"]))

            # Classify
            clf, reason = classify_variant(
                z=fit["z"], r2=fit["r2"],
                peak_stress=peak_stress_mean,
                collapse_cv=coll["collapse_cv"],
                z_ref=z_ref,
                thresholds=class_cfg,
            )

            fit_row = {
                "experiment":    exp_name,
                "variant":       variant,
                "z":             round(fit["z"], 4) if fit["fit_valid"] else np.nan,
                "z_ref":         z_ref,
                "delta_z":       round(abs(fit["z"] - z_ref), 4) if fit["fit_valid"] else np.nan,
                "r2":            round(fit["r2"], 4) if fit["fit_valid"] else np.nan,
                "z_stderr":      round(fit["z_stderr"], 4) if fit["fit_valid"] else np.nan,
                "n_L_points":    fit["n_points"],
                "fit_valid":     fit["fit_valid"],
                "peak_stress":   round(peak_stress_mean, 4),
                "peak_drift":    round(abs(peak_stress_mean - 0.9), 4),
                "classification": clf,
                "reason":        reason,
            }
            fit_rows.append(fit_row)

            coll_row = {
                "experiment":      exp_name,
                "variant":         variant,
                "collapse_cv":     round(coll["collapse_cv"], 4) if not np.isnan(coll["collapse_cv"]) else np.nan,
                "max_cv":          round(coll["max_cv"], 4) if not np.isnan(coll["max_cv"]) else np.nan,
                "collapse_status": _collapse_label(coll["collapse_cv"], fss_cfg),
                "z_used":          round(z_use, 4),
                "n_stress_points": coll["n_stress_points"],
            }
            collapse_rows.append(coll_row)

    # Assign universality level
    level, level_desc = assign_level(fit_rows, collapse_rows,
                                      cfg["classification"])

    # Save outputs
    _save_csv(fit_rows, output_dir / cfg["output"]["fit_table"],
              ["experiment","variant","z","z_ref","delta_z","r2","z_stderr",
               "n_L_points","fit_valid","peak_stress","peak_drift",
               "classification","reason"])

    _save_csv(collapse_rows, output_dir / cfg["output"]["collapse_metrics"],
              ["experiment","variant","collapse_cv","max_cv","collapse_status",
               "z_used","n_stress_points"])

    # Generate report
    report = _build_report(fit_rows, collapse_rows, level, level_desc, z_ref)
    report_path = output_dir / cfg["output"]["final_report"]
    with open(report_path, "w") as f:
        f.write(report)
    log.info(f"Final report → {report_path}")

    print(report)
    return fit_rows, collapse_rows, level


def _collapse_label(cv: float, fss_cfg: Dict) -> str:
    if np.isnan(cv):
        return "UNKNOWN"
    if cv <= fss_cfg["cv_good_collapse"]:
        return "GOOD_COLLAPSE"
    if cv <= fss_cfg["cv_partial_collapse"]:
        return "PARTIAL_COLLAPSE"
    return "POOR_COLLAPSE"


def _save_csv(rows: List[Dict], path: Path, fields: List[str]):
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    log.info(f"Saved {len(rows)} rows → {path}")


def _build_report(fit_rows, collapse_rows, level, level_desc, z_ref) -> str:
    lines = []
    lines.append("=" * 65)
    lines.append("  UNIVERSALITY VALIDATION PACK (UVP-01) — FINAL REPORT")
    lines.append("=" * 65)
    lines.append("")

    # Summary counts
    total   = len(fit_rows)
    n_pass  = sum(1 for r in fit_rows if r["classification"] == "PASS")
    n_cond  = sum(1 for r in fit_rows if r["classification"] == "CONDITIONAL_PASS")
    n_fail  = sum(1 for r in fit_rows if r["classification"] == "FAIL")
    pass_rate = (n_pass + n_cond) / total if total > 0 else 0

    lines.append(f"  Reference z (V18 baseline):  {z_ref}")
    lines.append(f"  Total variants tested:       {total}")
    lines.append(f"  PASS:                        {n_pass}")
    lines.append(f"  CONDITIONAL PASS:            {n_cond}")
    lines.append(f"  FAIL:                        {n_fail}")
    lines.append(f"  Overall pass rate:           {pass_rate:.1%}")
    lines.append("")
    lines.append(f"  ▶ UNIVERSALITY LEVEL:  Level {level}")
    lines.append(f"    {level_desc}")
    lines.append("")
    lines.append("=" * 65)

    # Per-experiment breakdown
    experiments = sorted(set(r["experiment"] for r in fit_rows))
    for exp in experiments:
        exp_rows = [r for r in fit_rows if r["experiment"] == exp]
        lines.append(f"\n  [{exp.upper()}]")
        lines.append(f"  {'Variant':<30} {'z':>7} {'Δz':>7} {'R²':>6} {'Peak':>6} {'Status'}")
        lines.append(f"  {'-'*30} {'-'*7} {'-'*7} {'-'*6} {'-'*6} {'-'*20}")
        for r in sorted(exp_rows, key=lambda x: x["variant"]):
            z_str   = f"{r['z']:.4f}"  if not np.isnan(r['z'])    else "N/A"
            dz_str  = f"{r['delta_z']:.4f}" if not np.isnan(r.get('delta_z', np.nan)) else "N/A"
            r2_str  = f"{r['r2']:.3f}" if not np.isnan(r['r2'])   else "N/A"
            pk_str  = f"{r['peak_stress']:.3f}"
            lines.append(
                f"  {r['variant']:<30} {z_str:>7} {dz_str:>7} {r2_str:>6} "
                f"{pk_str:>6}  {r['classification']}")

    # Collapse summary
    lines.append("\n" + "=" * 65)
    lines.append("  COLLAPSE METRICS SUMMARY")
    lines.append("=" * 65)
    lines.append(f"  {'Variant':<30} {'CV':>8} {'Status'}")
    lines.append(f"  {'-'*30} {'-'*8} {'-'*20}")
    for r in sorted(collapse_rows, key=lambda x: (x["experiment"], x["variant"])):
        cv_str = f"{r['collapse_cv']:.4f}" if not np.isnan(r.get("collapse_cv", np.nan)) else "N/A"
        lines.append(f"  {r['variant']:<30} {cv_str:>8}  {r['collapse_status']}")

    # Interpretation
    lines.append("\n" + "=" * 65)
    lines.append("  INTERPRETATION")
    lines.append("=" * 65)

    if level == 0:
        lines.append("  ✗ Scaling not yet established across perturbation variants.")
        lines.append("    → Review simulation parameters and re-run with increased n_runs.")
    elif level == 1:
        lines.append("  ✓ Level 1: Scaling confirmed within tested perturbation axes.")
        lines.append("    → Proceed to: (1) higher-p topology tests, (2) larger L.")
        lines.append("    → Not sufficient for universality class claim.")
    elif level == 2:
        lines.append("  ✓ Level 2: Multi-axis invariance demonstrated.")
        lines.append("    → Collapse quality and exponent stability are borderline.")
        lines.append("    → Recommended: improve collapse metric, add L > 320k.")
        lines.append("    → Approaching but not yet at universality claim threshold.")
    elif level == 3:
        lines.append("  ✓✓ Level 3: Strong universality evidence.")
        lines.append("    → Exponent stable across micro-rules AND topologies.")
        lines.append("    → Collapse quality acceptable.")
        lines.append("    → Sufficient basis for universality class claim in manuscript.")
        lines.append("    → Remaining step: analytical / RG backing for z ≈ 1.37.")

    lines.append("")
    lines.append("=" * 65)
    return "\n".join(lines)


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="UVP-01 Analysis Engine")
    parser.add_argument("--config", default="uvp_config.yaml")
    parser.add_argument("--input",  default=None,
                        help="Override input CSV path")
    args = parser.parse_args()

    with open(args.config) as f:
        cfg = yaml.safe_load(f)

    output_dir = Path(cfg["global"]["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.input:
        input_csv = Path(args.input)
    else:
        input_csv = output_dir / cfg["output"]["summary_results"]

    if not input_csv.exists():
        log.error(f"Input file not found: {input_csv}")
        log.error("Run run_uvp_experiments.py first.")
        sys.exit(1)

    analyze(cfg, input_csv, output_dir)


if __name__ == "__main__":
    main()
