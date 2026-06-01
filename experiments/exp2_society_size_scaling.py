"""Experiment 2: alpha_c(N) -- how the critical harmful-agent ratio scales
with society size N. Theory (paper §9.4) predicts alpha_c ~ Theta / N (or a
sub-linear power law), giving a straight line on a log-log plot.

Output: outputs/exp2_society_size_scaling/
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from experiments._common import (
    RunSpec, aggregate, exp_dir, run_grid, write_csv, write_json,
)


SCENARIO = "s1"
N_GRID = [100, 200, 500, 1000, 2000, 5000]
ALPHAS = [0.001, 0.002, 0.005, 0.01, 0.02, 0.03, 0.05, 0.08, 0.12, 0.20]
SEEDS = [1, 2, 3, 4, 5]


def estimate_alpha_c(rows, N, alphas, threshold: float = 0.5):
    """Linear interpolate alpha at which P(collapse)=threshold."""
    ps = []
    for a in alphas:
        agg = aggregate([r for r in rows if r["n_society"] == N and r["alpha"] == a],
                        ["alpha"], "collapse_rate")
        ps.append(agg.get((a,), {"mean": 0.0})["mean"])
    ps = np.array(ps)
    alphas = np.array(alphas)
    # find first index where p >= threshold
    idx = np.where(ps >= threshold)[0]
    if len(idx) == 0:
        return None, ps
    i = int(idx[0])
    if i == 0:
        return float(alphas[0]), ps
    # linear interpolate between i-1 and i
    p0, p1 = ps[i - 1], ps[i]
    a0, a1 = alphas[i - 1], alphas[i]
    if p1 == p0:
        return float(a1), ps
    ac = a0 + (threshold - p0) * (a1 - a0) / (p1 - p0)
    return float(ac), ps


def main():
    out = exp_dir("exp2_society_size_scaling")
    specs = [RunSpec(SCENARIO, N, a, s) for N in N_GRID for a in ALPHAS for s in SEEDS]
    print(f"Running {len(specs)} episodes for exp2...")
    rows = run_grid(specs)
    write_csv(rows, out / "data.csv")
    write_json({"scenario": SCENARIO, "alphas": ALPHAS, "n_grid": N_GRID, "seeds": SEEDS},
               out / "config.json")

    # ---------- estimate alpha_c per N ----------
    alpha_cs = []
    p_curves = {}
    for N in N_GRID:
        ac, ps = estimate_alpha_c(rows, N, ALPHAS)
        alpha_cs.append(ac)
        p_curves[N] = ps

    # ---------- Figure 1: log-log alpha_c vs N + power-law fit ----------
    fig, ax = plt.subplots(figsize=(7, 5))
    Ns = np.array([N for N, ac in zip(N_GRID, alpha_cs) if ac is not None])
    acs = np.array([ac for ac in alpha_cs if ac is not None])
    ax.loglog(Ns, acs, "o", markersize=8, color="C3", label="estimated α_c(N)")
    fit_info = {}
    if len(Ns) >= 2:
        # log alpha_c = log A + beta * log N
        beta, logA = np.polyfit(np.log(Ns), np.log(acs), 1)
        A = float(np.exp(logA))
        fit_x = np.logspace(np.log10(Ns.min()), np.log10(Ns.max()), 50)
        fit_y = A * fit_x ** beta
        ax.loglog(fit_x, fit_y, "--", color="C0",
                  label=f"fit  α_c ≈ {A:.3g}·N^{{{beta:.2f}}}")
        fit_info = {"A": A, "beta": float(beta)}
    ax.set_xlabel("Society size N (log)")
    ax.set_ylabel("Critical harmful ratio α_c (log)")
    ax.set_title("WolfBench S1: scaling of critical harmful ratio with society size")
    ax.grid(which="both", alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out / "alpha_critical_vs_N.png", dpi=140)
    plt.close(fig)

    # ---------- Figure 2: heatmap of P_collapse(N, alpha) ----------
    fig, ax = plt.subplots(figsize=(8, 5))
    grid = np.zeros((len(N_GRID), len(ALPHAS)))
    for i, N in enumerate(N_GRID):
        grid[i, :] = p_curves[N]
    im = ax.imshow(grid, aspect="auto", origin="lower",
                   extent=[0, len(ALPHAS), 0, len(N_GRID)],
                   cmap="magma", vmin=0, vmax=1)
    ax.set_xticks(np.arange(len(ALPHAS)) + 0.5)
    ax.set_xticklabels([f"{a:g}" for a in ALPHAS], rotation=45)
    ax.set_yticks(np.arange(len(N_GRID)) + 0.5)
    ax.set_yticklabels(N_GRID)
    ax.set_xlabel("α")
    ax.set_ylabel("N")
    ax.set_title("P(collapse) heatmap")
    fig.colorbar(im, ax=ax, label="P(collapse)")
    fig.tight_layout()
    fig.savefig(out / "p_collapse_heatmap.png", dpi=140)
    plt.close(fig)

    write_json({
        "alpha_critical": {str(N): ac for N, ac in zip(N_GRID, alpha_cs)},
        "fit": fit_info,
    }, out / "summary.json")
    print(f"Done. Wrote {out}")


if __name__ == "__main__":
    main()
