from __future__ import annotations

import argparse
from pathlib import Path

from uvp import run_pipeline
from uvp.io import load_config


def main() -> None:
    parser = argparse.ArgumentParser(description="Run UVP v2 pipeline")
    parser.add_argument("--config", required=True, help="Path to YAML config")
    args = parser.parse_args()

    cfg = load_config(args.config)
    result = run_pipeline(cfg)

    print("UVP run complete")
    for k, v in result.items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    main()
