from __future__ import annotations

from pathlib import Path

from .adapters import adapt_grid, adapt_llm
from .collapse import prepare_collapse
from .detect_critical import detect_critical
from .fit_z import fit_z_auto
from .io import ensure_dir, load_csv, save_dataframe, save_json, validate_schema
from .optional.relaxation import fit_relaxation_summary
from .plotting import plot_collapse, plot_scan, plot_z_curve
from .scan import compute_scan


def run_pipeline(config: dict) -> dict:
    input_path = config["input_path"]
    output_dir = ensure_dir(config.get("output_dir", "results/run"))
    source_type = config.get("source_type", "grid")
    col_cfg = config.get("columns", {})

    raw = load_csv(input_path)
    if source_type == "llm":
        df = adapt_llm(raw, columns=col_cfg)
    else:
        df = adapt_grid(raw, columns=col_cfg)

    validate_schema(df)
    save_dataframe(df, output_dir / "processed_input.csv")

    scan_df = compute_scan(df)
    save_dataframe(scan_df, output_dir / "sigma_scan" / "scan.csv")

    critical = detect_critical(scan_df, band_half_width_points=int(config.get("critical_detection", {}).get("band_half_width_points", 1)))
    save_json(critical, output_dir / "critical" / "sigma_c.json")

    z_result = fit_z_auto(df, critical["sigma_c"], cfg=config.get("z_fit", {}))
    save_json(z_result, output_dir / "z_fit" / "z_fit.json")

    collapse_df = prepare_collapse(df, sigma_c=critical["sigma_c"], z=z_result.get("z_best"))
    save_dataframe(collapse_df, output_dir / "collapse" / "collapse_data.csv")

    if config.get("plotting", {}).get("enabled", True):
        plot_scan(scan_df, critical["sigma_c"], output_dir / "figures" / "scan.png")
        plot_collapse(collapse_df, output_dir / "figures" / "collapse.png")
        plot_z_curve(z_result, output_dir / "figures" / "z_scan.png")

    if config.get("relaxation", {}).get("enabled", False) and "tau" in df.columns and df["tau"].dropna().size > 0:
        relax_df = fit_relaxation_summary(df)
        save_dataframe(relax_df, output_dir / "critical" / "relaxation_summary.csv")

    return {
        "output_dir": str(Path(output_dir).resolve()),
        "rows_in": int(len(raw)),
        "rows_processed": int(len(df)),
        "sigma_c": critical["sigma_c"],
        "critical_band": critical["critical_band"],
        "z_best": z_result.get("z_best"),
        "z_method": z_result.get("method"),
    }
