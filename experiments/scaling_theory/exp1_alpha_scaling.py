"""Experiment 1: P_collapse(alpha) at fixed N -- expect S-shaped curves with
shifting critical threshold alpha_c(N). Demonstrates the nonlinear
phase-transition claim.

Output: outputs/scaling_theory/exp1_alpha_scaling/
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from experiments._common import (
    RunSpec, aggregate, alpha_critical, run_grid, scaling_exp_dir, write_csv, write_json,
)


SCENARIO = "s1"
ALPHAS = [0.0, 0.001, 0.005, 0.0075, 0.01, 0.015, 0.02, 0.03, 0.05, 0.10, 0.20]
N_GRID = [200, 1000, 5000]
SEEDS = list(range(1, 21))


def main():
    out = scaling_exp_dir("exp1_alpha_scaling")
    specs = [RunSpec(SCENARIO, N, a, s) for N in N_GRID for a in ALPHAS for s in SEEDS]
    print(f"Running {len(specs)} episodes for exp1...")
    rows = run_grid(specs)
    write_csv(rows, out / "data.csv")
    write_json({"scenario": SCENARIO, "alphas": ALPHAS, "n_grid": N_GRID, "seeds": SEEDS},
               out / "config.json")

    # ---------- Figure 1: P_collapse vs alpha, one curve per N ----------
    fig, ax = plt.subplots(figsize=(7, 5))
    colours = plt.cm.viridis(np.linspace(0.15, 0.85, len(N_GRID)))
    summary = {}
    for N, c in zip(N_GRID, colours):
        means, stds = [], []
        for a in ALPHAS:
            agg = aggregate(
                [r for r in rows if r["n_society"] == N and r["alpha"] == a],
                ["alpha"], "collapse_rate")
            stat = agg.get((a,), {"mean": 0.0, "std": 0.0})
            means.append(stat["mean"])
            stds.append(stat["std"])
        means = np.array(means)
        stds = np.array(stds)
        ac = alpha_critical(rows, ALPHAS, N)
        summary[str(N)] = {"alpha_c": ac, "p_collapse": dict(zip(map(str, ALPHAS), means.tolist()))}
        ax.plot(ALPHAS, means, "-o", color=c, label=f"N={N}  α_c={ac}")
        ax.fill_between(ALPHAS,
                        np.clip(means - stds, 0, 1),
                        np.clip(means + stds, 0, 1),
                        color=c, alpha=0.15)
        if ac is not None:
            ax.axvline(ac, color=c, linestyle=":", alpha=0.6)
    ax.axhline(0.5, color="grey", linestyle="--", alpha=0.5, label="P=0.5")
    ax.set_xscale("symlog", linthresh=1e-3)
    ax.set_xlabel("Harmful-agent ratio α")
    ax.set_ylabel("P(collapse)  over 30-day episode")
    ax.set_title("WolfBench S1: nonlinear collapse vs harmful ratio\nat different society sizes")
    ax.set_ylim(-0.05, 1.05)
    ax.legend(loc="lower right")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(out / "p_collapse_vs_alpha.png", dpi=140)
    plt.close(fig)

    # ---------- Figure 2: companion harm metrics ----------
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
    for N, c in zip(N_GRID, colours):
        for ax, metric, title in zip(
            axes,
            ["max_collapse_score", "retail_loss_pct_30d", "social_cascade_peak"],
            ["max CollapseScore", "RetailLoss@30d (frac)", "SocialCascadePeak"],
        ):
            ms = []
            for a in ALPHAS:
                agg = aggregate(
                    [r for r in rows if r["n_society"] == N and r["alpha"] == a],
                    ["alpha"], metric)
                ms.append(agg.get((a,), {"mean": 0.0})["mean"])
            ax.plot(ALPHAS, ms, "-o", color=c, label=f"N={N}")
            ax.set_xscale("symlog", linthresh=1e-3)
            ax.set_xlabel("α")
            ax.set_title(title)
            ax.grid(alpha=0.3)
    axes[0].legend()
    fig.suptitle("WolfBench S1: per-α harm metrics across N", y=1.02)
    fig.tight_layout()
    fig.savefig(out / "metrics_vs_alpha.png", dpi=140, bbox_inches="tight")
    plt.close(fig)

    write_json(summary, out / "summary.json")
    print(f"Done. Wrote {out}")


if __name__ == "__main__":
    main()
