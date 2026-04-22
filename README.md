\# UVP v2: Universality Validation Pipeline for Bounded Criticality



A reproducible framework for detecting, comparing, and analyzing bounded criticality across complex systems.



\---



\## Overview



UVP v2 (Universality Validation Pipeline v2) is a unified analysis framework designed to test whether different complex systems exhibit a shared form of \*\*bounded criticality\*\*.



The pipeline is intended to transform heterogeneous simulation outputs into a standardized statistical-physics workflow, enabling:



\- critical-region detection

\- collapse-style comparison

\- dynamical exponent estimation

\- cross-system universality testing



UVP v2 is designed for use across both:



\- \*\*power-grid cascading-failure systems\*\*

\- \*\*LLM / AI multi-agent cascade systems\*\*



\---



\## Core Idea



Many complex systems do not exhibit purely divergent criticality.

Instead, they display a \*\*bounded critical regime\*\*:

a transition region with identifiable critical structure, but without unconstrained divergence.



UVP v2 provides a systematic way to test that hypothesis.



\---



\## Key Functions



\- \*\*Unified data adapters\*\* for heterogeneous simulation outputs

\- \*\*Critical region detection\*\* using configurable heuristics

\- \*\*Collapse-style analysis\*\* for comparing curves across system sizes or variants

\- \*\*Dynamical exponent estimation\*\* including proxy and tau-based approaches

\- \*\*End-to-end reproducibility\*\* from raw outputs to figures and summaries

\- \*\*Cross-system comparison\*\* between infrastructure systems and AI agent systems



\---



\## Research Object



\- \*\*Framework type:\*\* Universality validation pipeline

\- \*\*Primary target:\*\* Bounded criticality

\- \*\*Domains:\*\* Power grids, LLM multi-agent systems, complex adaptive systems

\- \*\*Inputs:\*\* Heterogeneous simulation outputs

\- \*\*Outputs:\*\* Critical-region summaries, scaling-style comparisons, exponent estimates, reproducible figures



\---



\## Why This Repository Exists



This repository is the \*\*method layer\*\* of the broader Bounded Criticality research program.



If `bounded-criticality-power-grids` is the application layer,

then `uvp-v2-framework` is the reusable validation and analysis layer.



It provides the machinery for testing whether bounded critical behavior is:



\- robust,

\- comparable across systems,

\- and potentially universal.



\---



\## Typical Workflow



```text

raw simulation data

→ standardized input format

→ critical region detection

→ collapse / alignment analysis

→ exponent estimation

→ publication-ready summaries

Quick Start



Clone the repository:



git clone https://github.com/Z139-Lab/uvp-v2-framework.git

cd uvp-v2-framework



Install dependencies:



pip install -r requirements.txt



Run your analysis pipeline according to the repository scripts and documentation.



Relation to Other Repositories

Power-grid application repo: https://github.com/Z139-Lab/bounded-criticality-power-grids

Research portal: https://github.com/Z139-Lab/bounded-criticality-portal

IEEE-2383 extreme-case study: https://github.com/Z139-Lab/ieee-2383-critical-edge

Key Terms



bounded criticality, universality validation, critical region detection, dynamical exponent, collapse analysis, complex systems, cascading failure, multi-agent systems, reproducible research



Recommended Use



Use UVP v2 when you want to:



compare bounded-critical behavior across multiple system sizes

test whether a transition is sharp, finite-width, or near-discontinuous

estimate dynamical signatures from heterogeneous simulations

build a reusable validation pipeline instead of a one-off analysis

Citation



Please add and use a repository-level CITATION.cff file for formal citation.



Author



Juan Adam

Independent Research


