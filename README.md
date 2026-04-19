# uvp-framework

A GitHub-ready **Universality Validation Pipeline (UVP)** for cross-system criticality analysis.

This repo is structured to turn a mixed analysis workflow into a reproducible framework:

- load CSV data from grid, UVP summaries, or LLM experiments
- normalize each dataset into a canonical schema
- scan stress × system-size structure
- detect a heuristic critical point / critical band
- prepare collapse-style outputs
- estimate a provisional dynamical exponent `z`
- save JSON / CSV / figures for paper workflows

## What is included in this package

This package already includes three example real inputs:

- `data/raw/grid/summary_results.csv` → main multi-`L` UVP summary table
- `data/raw/grid/micro_rule_summary_results.csv` → micro-rule robustness table
- `data/raw/grid/probe_summary.csv` → probe / transition scan table

## Canonical schema

After normalization, UVP works with these columns:

- `stress`
- `L`
- `phi`
- `collapse_prob` (may be a proxy when raw collapse is unavailable)
- `tau` (optional)
- `n_seeds` (optional)

Additional metadata columns are preserved when present, such as `chi`, `phi_var`, `cv`, `topology`, `variant`, and `regime`.

## Included configs

- `configs/demo_toy.yaml` → minimal demo run
- `configs/grid_default.yaml` → main `summary_results.csv`
- `configs/grid_micro_rule.yaml` → micro-rule robustness
- `configs/grid_probe.yaml` → probe / transition scan
- `configs/llm_default.yaml` → placeholder for future LLM integration

## Quick start

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Run the toy demo:

```bash
python run_uvp.py --config configs/demo_toy.yaml
```

Run the main multi-`L` summary:

```bash
python run_uvp.py --config configs/grid_default.yaml
```

Run the micro-rule robustness dataset:

```bash
python run_uvp.py --config configs/grid_micro_rule.yaml
```

Run the probe dataset:

```bash
python run_uvp.py --config configs/grid_probe.yaml
```

## Expected outputs

Each run writes into its configured `output_dir`, including:

- `processed_input.csv`
- `sigma_scan/scan.csv`
- `critical/sigma_c.json`
- `collapse/collapse_data.csv`
- `z_fit/z_fit.json`
- `figures/scan.png`
- `figures/collapse.png`
- `figures/z_scan.png` (when applicable)

## Scientific status

This version is intended as a **framework foundation**, not a final claim engine.

Important caveats:

- critical detection is still heuristic (`composite_scan`)
- if `tau` is unavailable, `z` falls back to a proxy collapse scan
- single-`L` inputs can produce phase-scan outputs but **cannot support a meaningful multi-size `z` estimate**

That means:

- `summary_results.csv` is the best current input for `z`-style analysis
- `micro_rule_summary_results.csv` is best for robustness / invariance checks
- `probe_summary.csv` is best for phase / transition storytelling, not for main universality claims

## PowerShell smoke test

From the repo root:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_test.ps1
```

## Upload to GitHub

```bash
git init
git add .
git commit -m "Initial UVP v2 framework"
```

Then create an empty GitHub repo and run:

```bash
git remote add origin <YOUR_GITHUB_REPO_URL>
git branch -M main
git push -u origin main
```


## Step-by-step PowerShell test

```powershell
cd "C:\Users\JUAN\Desktop\uvp-framework"
python -m pip install -r .\requirements.txt
python .\run_uvp.py --config .\configs\demo_toy.yaml
python .\run_uvp.py --config .\configs\grid_default.yaml
python .\run_uvp.py --config .\configs\grid_micro_rule.yaml
python .\run_uvp.py --config .\configs\grid_probe.yaml
```

Or run the bundled PowerShell helper:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup_and_test.ps1
```
