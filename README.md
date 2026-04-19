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

