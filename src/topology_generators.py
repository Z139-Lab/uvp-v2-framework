"""
topology_generators.py
======================
Network topology generators for UVP-01.

Each generator returns a list of adjacency sets (neighbour lists) for
L agents, plus a metadata dict.

Topologies:
  - chain:        1D ring lattice (baseline)
  - small_world:  Watts-Strogatz small-world
  - scale_free:   Barabási-Albert preferential attachment
  - random_er:    Erdős-Rényi random graph (control)
  - fully_connected: mean-field limit (control)
"""

import numpy as np
import networkx as nx
from typing import List, Set, Dict, Tuple, Any


# ─────────────────────────────────────────────
# TYPE ALIAS
# ─────────────────────────────────────────────
AdjList = List[Set[int]]   # index i → set of neighbour indices


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def _nx_to_adjlist(G: nx.Graph) -> AdjList:
    n = G.number_of_nodes()
    adj: AdjList = [set() for _ in range(n)]
    for u, v in G.edges():
        adj[u].add(v)
        adj[v].add(u)
    return adj


def _graph_stats(G: nx.Graph) -> Dict[str, Any]:
    degrees = [d for _, d in G.degree()]
    return {
        "n_nodes":    G.number_of_nodes(),
        "n_edges":    G.number_of_edges(),
        "mean_degree": float(np.mean(degrees)),
        "max_degree":  int(np.max(degrees)),
        "density":     nx.density(G),
    }


# ─────────────────────────────────────────────
# TOPOLOGY GENERATORS
# ─────────────────────────────────────────────

def chain_topology(L: int, k: int = 2, seed: int = 42) -> Tuple[AdjList, Dict]:
    """
    1D ring lattice: each node connected to k nearest neighbours on each side.
    Default k=2 → each node has 4 neighbours (2 left, 2 right).
    This is the V18 baseline topology.
    """
    G = nx.watts_strogatz_graph(L, 2 * k, 0.0, seed=seed)  # p=0 → no rewiring
    meta = _graph_stats(G)
    meta["topology"] = "chain"
    meta["params"]   = {"k": k}
    return _nx_to_adjlist(G), meta


def small_world_topology(L: int, k: int = 4, p: float = 0.1,
                          seed: int = 42) -> Tuple[AdjList, Dict]:
    """
    Watts-Strogatz small-world network.
    k: number of nearest neighbours in ring lattice before rewiring
    p: rewiring probability (0 = ring, 1 = random)
    """
    G = nx.watts_strogatz_graph(L, k, p, seed=seed)
    meta = _graph_stats(G)
    meta["topology"] = "small_world"
    meta["params"]   = {"k": k, "p": p}
    return _nx_to_adjlist(G), meta


def scale_free_topology(L: int, m: int = 2,
                         seed: int = 42) -> Tuple[AdjList, Dict]:
    """
    Barabási-Albert preferential attachment.
    m: number of edges to attach from new node to existing nodes.
    Produces power-law degree distribution P(k) ~ k^(-3).
    """
    G = nx.barabasi_albert_graph(L, m, seed=seed)
    meta = _graph_stats(G)
    meta["topology"] = "scale_free"
    meta["params"]   = {"m": m}
    return _nx_to_adjlist(G), meta


def random_er_topology(L: int, p: float = 0.004,
                        seed: int = 42) -> Tuple[AdjList, Dict]:
    """
    Erdős-Rényi random graph. Control topology.
    p chosen to give ~same mean degree as chain (k=2 → mean_deg≈4).
    """
    rng = np.random.default_rng(seed)
    G   = nx.erdos_renyi_graph(L, p, seed=int(rng.integers(1e9)))
    meta = _graph_stats(G)
    meta["topology"] = "random_er"
    meta["params"]   = {"p": p}
    return _nx_to_adjlist(G), meta


def fully_connected_topology(L: int, **_) -> Tuple[AdjList, Dict]:
    """
    Complete graph — mean-field limit.
    Only usable for small L (expensive for L > ~5k).
    """
    G = nx.complete_graph(L)
    meta = _graph_stats(G)
    meta["topology"] = "fully_connected"
    meta["params"]   = {}
    return _nx_to_adjlist(G), meta


# ─────────────────────────────────────────────
# REGISTRY
# ─────────────────────────────────────────────

TOPOLOGY_REGISTRY = {
    "chain":            chain_topology,
    "small_world":      small_world_topology,
    "scale_free":       scale_free_topology,
    "random_er":        random_er_topology,
    "fully_connected":  fully_connected_topology,
}


def get_topology(name: str, L: int, seed: int = 42, **kwargs) -> Tuple[AdjList, Dict]:
    """Unified topology factory."""
    if name not in TOPOLOGY_REGISTRY:
        raise ValueError(f"Unknown topology '{name}'. Available: {list(TOPOLOGY_REGISTRY)}")
    return TOPOLOGY_REGISTRY[name](L=L, seed=seed, **kwargs)


def get_uvp_topologies(L: int, seed: int = 42) -> Dict[str, Tuple[AdjList, Dict]]:
    """
    Returns all topologies used in the UVP-01 invariance test.
    For large L, skips fully_connected.
    """
    topologies = {}
    configs = [
        ("chain",       {}),
        ("small_world", {"k": 4, "p": 0.1}),
        ("small_world_high_p", {"k": 4, "p": 0.5}),
        ("scale_free",  {"m": 2}),
        ("scale_free_dense", {"m": 4}),
        ("random_er",   {"p": max(4.0 / L, 1e-4)}),
    ]
    for name, kwargs in configs:
        base_name = name
        topo_fn_name = name if name in TOPOLOGY_REGISTRY else name.rsplit("_", 1)[0]
        try:
            adj, meta = get_topology(topo_fn_name, L=L, seed=seed, **kwargs)
            meta["config_name"] = base_name
            topologies[base_name] = (adj, meta)
        except Exception as e:
            print(f"[topology_generators] Skipping {name}: {e}")
    return topologies


# ─────────────────────────────────────────────
# STRESS PROPAGATION WEIGHTS
# ─────────────────────────────────────────────

def get_propagation_weights(adj: AdjList, mode: str = "uniform") -> List[Dict[int, float]]:
    """
    Returns per-edge propagation weights for stress diffusion.

    Modes:
      uniform:  equal weight to all neighbours (default)
      degree:   weight inversely proportional to neighbour degree
      random:   random weights normalised per node
    """
    L = len(adj)
    weights = []
    for i in range(L):
        nbrs = list(adj[i])
        if not nbrs:
            weights.append({})
            continue
        if mode == "uniform":
            w = {j: 1.0 / len(nbrs) for j in nbrs}
        elif mode == "degree":
            raw = {j: 1.0 / max(len(adj[j]), 1) for j in nbrs}
            total = sum(raw.values())
            w = {j: v / total for j, v in raw.items()}
        elif mode == "random":
            vals = np.random.default_rng(i).random(len(nbrs))
            vals /= vals.sum()
            w = dict(zip(nbrs, vals.tolist()))
        else:
            raise ValueError(f"Unknown propagation weight mode: {mode}")
        weights.append(w)
    return weights


if __name__ == "__main__":
    for topo_name in ["chain", "small_world", "scale_free", "random_er"]:
        adj, meta = get_topology(topo_name, L=1000, seed=0)
        print(f"{topo_name:20s}  nodes={meta['n_nodes']}  "
              f"edges={meta['n_edges']}  mean_deg={meta['mean_degree']:.2f}  "
              f"density={meta['density']:.4f}")
