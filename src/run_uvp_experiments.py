print("🔥 NEW VERSION RUNNING 🔥")

import argparse
import csv
import json
import logging
import sys
import time
from pathlib import Path

import numpy as np
import yaml

# Local imports
sys.path.insert(0, str(Path(__file__).parent))
from micro_rule_variants import MicroRuleEngine
from topology_generators import get_topology

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

SUMMARY_FIELDS = [
    "experiment", "variant", "job_key", "L", "stress", "chi",
    "phi_mean", "phi_var", "cv", "topology", "topo_params",
    "n_runs", "engine_config", "elapsed_sec",
]


# =========================
# CORE SIMULATION
# =========================
def run_single_cascade(L, stress, engine, adj, n_steps=None, seed=0):
    if n_steps is None:
        n_steps = max(50, int(np.log2(L) * 10))

    rng = np.random.default_rng(seed)
    engine.rng = np.random.default_rng(seed + 1)

    local_stress = rng.uniform(0, stress, size=L)
    memory = np.zeros(L)

    # 只放 1 個初始失敗 seed，避免整個系統一開始就被推進全崩相
    failed = np.zeros(L, dtype=bool)
    initial_fail = rng.choice(L, size=1, replace=False)
    failed[initial_fail] = True

    for _ in range(n_steps):
        if failed.all():
            break

        new_failures = np.zeros(L, dtype=bool)

        for i in range(L):
            if failed[i]:
                continue

            memory[i] = engine.update_memory(local_stress[i], memory[i])

            # 降低放大倍率，避免 failure probability 過強
            p = engine.failure_prob(memory[i])
            p = min(1.0, p * 1.2)

            if engine.rng.random() < p:
                new_failures[i] = True

        for i in np.where(new_failures)[0]:
            failed[i] = True
            nbrs = adj[i]

            if nbrs:
                # 降低傳播強度，避免一觸即發全域崩潰
                propagation = stress * 0.15 / len(nbrs)

                for j in nbrs:
                    if not failed[j]:
                        local_stress[j] = min(1.0, local_stress[j] + propagation)

    # 注意：phi 這裡代表的是 failed fraction
    return float(np.mean(failed))


def run_condition(**job):
    t0 = time.time()

    try:
        engine = MicroRuleEngine(
            activation_name=job["engine_config"]["activation"],
            memory_name=job["engine_config"]["memory"],
            noise_name=job["engine_config"]["noise"],
            seed=job["seed_base"],
        )
    except Exception as e:
        print("ENGINE INIT ERROR:", e)
        return None

    try:
        adj, _ = get_topology(
            job["topology_name"],
            L=job["L"],
            seed=job["seed_base"],
            **job["topology_params"],
        )
    except Exception as e:
        print("TOPOLOGY ERROR:", e)
        return None

    phis = []

    for i in range(job["n_runs"]):
        try:
            phi = run_single_cascade(
                L=job["L"],
                stress=job["stress"],
                engine=engine,
                adj=adj,
                seed=job["seed_base"] + i * 7 + 1,
            )
            phis.append(phi)
        except Exception as e:
            print("RUN ERROR:", e)
            return None

    phis = np.array(phis)

    phi_mean = float(np.mean(phis))
    phi_var = float(np.var(phis))
    chi = job["L"] * phi_var

    return {
        "experiment": job["experiment"],
        "variant": job["variant"],
        "job_key": job["job_key"],
        "L": job["L"],
        "stress": job["stress"],
        "chi": chi,
        "phi_mean": phi_mean,
        "phi_var": phi_var,
        "cv": float(np.std(phis) / phi_mean) if phi_mean > 1e-12 else 0.0,
        "topology": job["topology_name"],
        "topo_params": json.dumps(job["topology_params"]),
        "n_runs": job["n_runs"],
        "engine_config": json.dumps(job["engine_config"]),
        "elapsed_sec": round(time.time() - t0, 4),
    }


# =========================
# JOB BUILDER
# =========================
def build_micro_rule_jobs(cfg):
    exp = cfg["micro_rule_experiment"]
    sizes = exp["system_sizes"]
    stresses = np.linspace(*exp["stress_window"], exp["n_stress_points"])

    variants = [{"name": "baseline", **exp["baseline"]}]

    jobs = []
    for v in variants:
        engine_cfg = {
            "activation": v["activation"],
            "memory": v["memory"],
            "noise": v["noise"],
        }

        for L in sizes:
            for s in stresses:
                jobs.append({
                    "L": L,
                    "stress": float(s),
                    "n_runs": exp["n_runs"],
                    "engine_config": engine_cfg,
                    "topology_name": exp["topology"],
                    "topology_params": {},
                    "seed_base": cfg["global"]["seed_base"],
                    "variant": v["name"],
                    "experiment": "micro_rule",
                    "job_key": f"{v['name']}_{L}_{s}",
                })

    return jobs


# =========================
# YAML LOADER
# =========================
def load_yaml_config(path):
    for enc in ("utf-8-sig", "utf-8", "cp1252"):
        try:
            with open(path, "r", encoding=enc) as f:
                return yaml.safe_load(f)
        except UnicodeDecodeError:
            continue
    raise RuntimeError(f"Cannot decode config file: {path}")


# =========================
# SAVE CSV
# =========================
def save_results_csv(results, out_path):
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with open(out_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=SUMMARY_FIELDS)
        writer.writeheader()
        writer.writerows(results)


# =========================
# MAIN
# =========================
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="uvp_config.yaml")
    args = parser.parse_args()

    print(f"\nLoading config: {args.config}")

    cfg = load_yaml_config(args.config)
    print("Config loaded")

    jobs = build_micro_rule_jobs(cfg)
    print(f"Jobs built: {len(jobs)}")

    output_dir = Path(cfg["global"]["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)

    out_csv = output_dir / "micro_rule_summary_results.csv"

    results = []

    for i, job in enumerate(jobs, start=1):
        print(f"\nRunning {i}/{len(jobs)} | L={job['L']} stress={job['stress']:.6f}")

        row = run_condition(**job)
        if row:
            results.append(row)

    print("\nDONE")
    print("rows:", len(results))

    if results:
        save_results_csv(results, out_csv)
        print(f"Saved to: {out_csv.resolve()}")
    else:
        print("No results saved")


if __name__ == "__main__":
    main()