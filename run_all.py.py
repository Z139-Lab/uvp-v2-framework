# run_all.py

print("Running UVP full reproduction pipeline...")

import os

# Step 1: run experiments
os.system("python src/run_uvp_experiments.py")

# Step 2: analyze
os.system("python src/analyze_uvp_results.py")

# Step 3: plot
os.system("python scripts/plot_figure2.py")

print("Done. Figures saved in results/figures/")