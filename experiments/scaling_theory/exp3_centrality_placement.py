"""Experiment 3: centrality vs random placement of harmful agents (S2).

At fixed alpha, plug harmful finfluencers into either random nodes or
high-degree hubs, and compare collapse outcomes. Demonstrates the
"centrality-harm elasticity" effect (paper §10 Social Experiment 1).

Output: outputs/scaling_theory/exp3_centrality_placement/
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from experiments._common import (
    RunSpec, aggregate, run_grid, scaling_exp_dir, write_csv, write_json,
)


SCENARIO = "s2"
ALPHA = 0.003
N_GRID = [500, 2000]
PLACEMENTS = ["random", "high_degree"]
SEEDS = [1, 2, 3, 4, 5, 6, 7, 8]


def main():
    out = scaling_exp_dir("exp3_centrality_placement")
    specs = []
    for N in N_GRID:
        for p in PLACEMENTS:
            for s in SEEDS:
                specs.append(RunSpec(SCENARIO, N, ALPHA, s, placement=p, label=p))
    print(f"Running {len(specs)} episodes for exp3...")
    rows = run_grid(specs)
    write_csv(rows, out / "data.csv")
    write_json({"scenario": SCENARIO, "alpha": ALPHA, "n_grid": N_GRID,
                "placements": PLACEMENTS, "seeds": SEEDS},
               out / "config.json")

    metrics = ["collapse_rate", "max_collapse_score",
               "retail_loss_pct_30d", "social_cascade_peak"]
    titles = ["P(collapse)", "max CollapseScore",
              "RetailLoss@30d", "SocialCascadePeak"]

    fig, axes = plt.subplots(1, len(metrics), figsize=(4.0 * len(metrics), 4.5))
    width = 0.35
    x = np.arange(len(N_GRID))
    summary = {}
    for ax, metric, title in zip(axes, metrics, titles):
        for j, p in enumerate(PLACEMENTS):
            means, stds = [], []
            for N in N_GRID:
                rows_sel = [r for r in rows if r["n_society"] == N and r["placement"] == p]
                vals = np.array([r[metric] for r in rows_sel])
                means.append(float(vals.mean()))
                stds.append(float(vals.std()))
                summary.setdefault(metric, {}).setdefault(str(N), {})[p] = {
                    "mean": float(vals.mean()), "std": float(vals.std()),
                }
            ax.bar(x + (j - 0.5) * width, means, width, yerr=stds, capsize=4,
                   label=p, color=f"C{j}", alpha=0.85)
        ax.set_xticks(x)
        ax.set_xticklabels([f"N={N}" for N in N_GRID])
        ax.set_title(title)
        ax.grid(axis="y", alpha=0.3)
    axes[0].legend(title="placement")
    fig.suptitle(f"WolfBench S2 (Finfluencer): random vs high-degree placement at α={ALPHA}", y=1.02)
    fig.tight_layout()
    fig.savefig(out / "centrality_compare.png", dpi=140, bbox_inches="tight")
    plt.close(fig)

    write_json(summary, out / "summary.json")
    print(f"Done. Wrote {out}")


if __name__ == "__main__":
    main()
