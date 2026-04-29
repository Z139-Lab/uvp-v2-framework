\# UVP v2: Universality Validation Pipeline for Bounded Criticality



A reproducible framework for detecting, comparing, and analyzing bounded criticality across complex systems.



\---



\## 🔁 Reproduce Main Results (One Command)



```bash

pip install -r requirements.txt

python run\\\_uvp.py --config configs/grid\\\_default.yaml



Outputs:



Critical region detection

Collapse-style analysis

Dynamical exponent estimation (z)

Publication-ready figures (saved in results/)

Overview



UVP v2 (Universality Validation Pipeline v2) is a unified analysis framework designed to test whether different complex systems exhibit a shared form of bounded criticality.



The pipeline transforms heterogeneous simulation outputs into a standardized statistical-physics workflow, enabling:



critical-region detection

collapse-style comparison

dynamical exponent estimation

cross-system universality testing



UVP v2 is designed for use across:



power-grid cascading-failure systems

LLM / AI multi-agent cascade systems

Core Idea



Many complex systems do not exhibit purely divergent criticality.

Instead, they display a bounded critical regime:



a transition region with identifiable critical structure, but without unconstrained divergence.



UVP v2 provides a systematic framework to detect and analyze this regime.



Pipeline

raw data 

→ normalization 

→ stress scan 

→ critical detection 

→ collapse analysis 

→ z estimation

→ publication-ready outputs

Key Functions

Unified data adapters for heterogeneous simulation outputs

Critical region detection using configurable heuristics

Collapse-style analysis across system sizes or variants

Dynamical exponent estimation (proxy-based and tau-based)

End-to-end reproducibility from raw data to figures

Cross-system comparison (infrastructure systems vs AI agent systems)

Input Schema (Canonical Representation)



All datasets are mapped to a unified schema:



stress

L (system size)

phi (observable)

collapse\\\_prob (optional)

tau (optional)

n\\\_seeds (optional)



Additional metadata (e.g., chi, cv, variant, topology) are preserved.



Expected Outputs



Each run produces:



processed\\\_input.csv

sigma\\\_scan/scan.csv

critical/sigma\\\_c.json

collapse/collapse\\\_data.csv

z\\\_fit/z\\\_fit.json

figures/scan.png

figures/collapse.png

figures/z\\\_scan.png

Scientific Scope



UVP v2 is designed to investigate:



finite-width critical bands vs classical phase transitions

robustness under micro-rule and topology perturbations

cross-system universality of bounded criticality

scaling behavior across heterogeneous systems

Current Status



This repository provides a framework layer, not a finalized claim engine.



Limitations:



critical detection is heuristic-based

z estimation depends on data richness

collapse quality is not yet fully optimized

Typical Workflow

raw simulation data

→ standardized input format

→ critical region detection

→ collapse analysis

→ exponent estimation

→ publication-ready summaries

Relation to Other Repositories

Power-grid application:

https://github.com/Z139-Lab/bounded-criticality-power-grids

Research portal:

https://github.com/Z139-Lab/bounded-criticality-portal

IEEE-2383 case study:

https://github.com/Z139-Lab/ieee-2383-critical-edge

Recommended Use



Use UVP v2 when you want to:



compare bounded-critical behavior across systems

distinguish sharp vs finite-width transitions

estimate dynamical scaling behavior

build reproducible, publication-grade analysis pipelines

Reproducibility



All results are reproducible via:



python run\\\_uvp.py --config configs/grid\\\_default.yaml



The pipeline produces deterministic outputs given fixed seeds and configuration.



Citation



Please use the included CITATION.cff file for formal citation.



Author



Juan Adam

Independent Research


