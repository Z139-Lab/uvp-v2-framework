\# UVP v2 Framework

\*\*Universality Validation Pipeline for Cross-System Criticality Analysis\*\*



A reproducible pipeline for detecting and comparing critical behavior across complex systems, including power grids, agent cascades, and synthetic models.



\---



\## Core Idea



This repository implements a unified workflow to:



\- detect critical regions (σ\_c or finite-width bands)

\- perform collapse-style transformations

\- estimate scaling behavior across system sizes

\- test robustness under rule and topology perturbations



The goal is to transform heterogeneous simulation outputs into a \*\*comparable statistical physics representation\*\*.



\---



\## Pipeline





raw data → normalization → stress scan → critical detection → collapse → z estimation





\---



\## Canonical Schema



All inputs are mapped to:





stress

L

phi

collapse\_prob (optional / proxy)

tau (optional)

n\_seeds (optional)





Additional metadata (e.g., `chi`, `phi\_var`, `cv`, `variant`, `topology`) are preserved.



\---



\## Included Datasets



This package includes three representative inputs:



\- `data/raw/grid/summary\_results.csv`  

&#x20; → multi-system summary (best for scaling analysis)



\- `data/raw/grid/micro\_rule\_summary\_results.csv`  

&#x20; → micro-rule robustness dataset



\- `data/raw/grid/probe\_summary.csv`  

&#x20; → transition / collapse behavior (phase scan)



\---



\## Quick Start



Install dependencies:



```bash

python -m pip install -r requirements.txt



Run demo:



python run\_uvp.py --config configs/demo\_toy.yaml



Run main dataset:



python run\_uvp.py --config configs/grid\_default.yaml

Demo (30 seconds)

python run\_uvp.py --config configs/grid\_default.yaml



Output:



results/grid\_main16/z\_fit/z\_fit.json

Expected Outputs



Each run produces:



processed\_input.csv

sigma\_scan/scan.csv

critical/sigma\_c.json

collapse/collapse\_data.csv

z\_fit/z\_fit.json

figures/scan.png

figures/collapse.png

figures/z\_scan.png

Scientific Interpretation



This framework distinguishes between three roles of data:



Dataset	Role

summary\_results	scaling / exponent estimation

micro\_rule	universality robustness

probe	phase / transition structure



Important:



meaningful z estimation requires multiple system sizes (L)

single-system data produces phase scans, not scaling laws

absence of tau triggers a proxy-based estimation

Current Status



This repository provides a framework foundation, not a final claim engine.



Limitations:



critical detection is heuristic (composite scan)

z estimation depends on data richness

collapse quality is not yet quantitatively optimized

Research Direction



The framework is designed to support investigations of:



finite-width critical bands vs classical phase transitions

scaling exponents under different dynamics

cross-system universality (e.g., grids vs agent cascades)

GitHub Usage

git init

git add .

git commit -m "Initial UVP v2 framework"

git remote add origin <YOUR\_REPO>

git branch -M main

git push -u origin main

PowerShell Quick Test

cd "C:\\Users\\JUAN\\Desktop\\uvp-framework"



python -m pip install -r .\\requirements.txt



python .\\run\_uvp.py --config .\\configs\\demo\_toy.yaml

python .\\run\_uvp.py --config .\\configs\\grid\_default.yaml



Or:



powershell -ExecutionPolicy Bypass -File .\\scripts\\setup\_and\_test.ps1


---

## Reproducibility

To reproduce the main results used in the paper:

`ash
python run_uvp.py --config configs/grid_default.yaml

Key outputs:

results/grid_main16/z_fit/z_fit.json
results/grid_main16/critical/sigma_c.json


---

## Highlight Result

A representative scaling analysis in this framework yields a **provisional dynamical exponent**

**z � 1.39**

This value should currently be interpreted as a framework-level research signal rather than a final universal claim. Its scientific role in the present repository is:

- to demonstrate that the UVP pipeline can recover nontrivial scaling structure
- to support comparison across datasets and perturbation classes
- to provide a reproducible entry point for later, stricter exponent estimation

---

## Figure-to-Workflow Mapping

The repository is organized so that major paper figures can be mapped onto explicit configs and outputs.

### Figure A � Main multi-L scaling analysis
Run:

`ash
python run_uvp.py --config configs/grid_default.yaml

Outputs:

results/grid_main16/processed_input.csv
results/grid_main16/sigma_scan/scan.csv
results/grid_main16/critical/sigma_c.json
results/grid_main16/collapse/collapse_data.csv
results/grid_main16/z_fit/z_fit.json
results/grid_main16/figures/scan.png
results/grid_main16/figures/collapse.png
results/grid_main16/figures/z_scan.png
Figure B � Micro-rule robustness / invariance check

Run:

python run_uvp.py --config configs/grid_micro_rule.yaml

Outputs:

results/grid_micro_rule/processed_input.csv
results/grid_micro_rule/sigma_scan/scan.csv
results/grid_micro_rule/critical/sigma_c.json
results/grid_micro_rule/collapse/collapse_data.csv
results/grid_micro_rule/z_fit/z_fit.json
Figure C � Probe / transition structure

Run:

python run_uvp.py --config configs/grid_probe.yaml

Outputs:

results/grid_probe/processed_input.csv
results/grid_probe/sigma_scan/scan.csv
results/grid_probe/critical/sigma_c.json
results/grid_probe/figures/scan.png
Methods-to-Repository Mapping

This section maps conceptual steps in the paper to concrete repository components.

1. Data normalization

Purpose:
Convert heterogeneous raw outputs into a canonical schema suitable for cross-system analysis.

Relevant files:

uvp/adapters/grid_adapter.py
uvp/adapters/llm_adapter.py

Canonical schema:

stress
L
phi
collapse_prob
tau
n_seeds
2. Stress scan and critical-region detection

Purpose:
Identify candidate critical points or finite-width transition bands.

Relevant files:

uvp/scan.py
uvp/detect_critical.py

Primary outputs:

sigma_scan/scan.csv
critical/sigma_c.json
3. Collapse-style transformation

Purpose:
Prepare scaled data products for cross-size comparison.

Relevant files:

uvp/collapse.py
uvp/metrics.py

Primary outputs:

collapse/collapse_data.csv
figures/collapse.png
4. Provisional exponent estimation

Purpose:
Estimate a provisional dynamical exponent z from available scaling structure.

Relevant files:

uvp/fit_z.py
uvp/metrics.py

Primary outputs:

z_fit/z_fit.json
figures/z_scan.png
5. Optional relaxation analysis

Purpose:
Support future integration of explicit relaxation-time analysis when tau is available.

Relevant files:

uvp/optional/relaxation.py
Citation / Versioning

For paper use, the recommended reference state of this repository is the tagged release:

v1.0-paper

Suggested paper wording:

Code and data used for the reproducible UVP workflow are available at the repository corresponding to version v1.0-paper.

