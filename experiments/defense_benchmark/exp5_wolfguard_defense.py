"""Experiment 5: WolfGuard defence shifts alpha_c (paper §5).

Compare P_collapse(alpha) with and without WolfGuard at fixed N. A successful
defence should push the critical threshold rightwards.

Output: outputs/defense_benchmark/exp5_wolfguard_defense/
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from experiments._common import (
    RunSpec, aggregate, alpha_critical, benchmark_exp_dir, run_grid, write_csv, write_json,
)
from wolfbench.tracks.runner import calibrate_clean_baseline


SCENARIO = "s1"
N_SOCIETY = 1000
ALPHAS = [0.0, 0.005, 0.01, 0.02, 0.05, 0.10, 0.20]
SEEDS = [1, 2, 3, 4, 5]


def main():
    out = benchmark_exp_dir("exp5_wolfguard_defense")
    print("Calibrating WolfGuard baseline from S0...")
    baseline = calibrate_clean_baseline(n_society=min(N_SOCIETY, 1000),
                                        seeds=(1, 2, 3))

    specs = []
    for defence in (False, True):
        for a in ALPHAS:
            for s in SEEDS:
                specs.append(RunSpec(SCENARIO, N_SOCIETY, a, s,
                                     defense=defence,
                                     label="defended" if defence else "no_def"))
    print(f"Running {len(specs)} episodes for exp5...")
    # Episodes with defense need baseline for z-scoring
    def runner():
        from experiments._common import run_episode
        rows = []
        for i, s in enumerate(specs, 1):
            rows.append(run_episode(s, baseline=baseline if s.defense else None))
            if i % 10 == 0 or i == len(specs):
                print(f"  [{i}/{len(specs)}]")
        return rows

    rows = runner()
    write_csv(rows, out / "data.csv")
    write_json({"scenario": SCENARIO, "alphas": ALPHAS,
                "n_society": N_SOCIETY, "seeds": SEEDS},
               out / "config.json")

    # ---------- Figure: P_collapse curves with vs without defense ----------
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    ax = axes[0]
    summary = {}
    for label, defended, c in [("no defense", 0, "C3"), ("WolfGuard", 1, "C0")]:
        means, stds = [], []
        for a in ALPHAS:
            sel = [r for r in rows if r["alpha"] == a and r["defense"] == defended]
            vals = np.array([r["collapse_rate"] for r in sel])
            means.append(float(vals.mean()))
            stds.append(float(vals.std()))
        means = np.array(means)
        stds = np.array(stds)
        ax.plot(ALPHAS, means, "-o", color=c, label=label)
        ax.fill_between(ALPHAS,
                        np.clip(means - stds, 0, 1),
                        np.clip(means + stds, 0, 1),
                        color=c, alpha=0.2)
        ac = alpha_critical(
            [r for r in rows if r["defense"] == defended], ALPHAS, N_SOCIETY)
        if ac is not None:
            ax.axvline(ac, color=c, linestyle=":", alpha=0.6)
        summary[label] = {"alpha_c": ac,
                          "p_collapse": dict(zip(map(str, ALPHAS), means.tolist()))}
    ax.axhline(0.5, color="grey", linestyle="--", alpha=0.5)
    ax.set_xscale("symlog", linthresh=1e-3)
    ax.set_xlabel("α")
    ax.set_ylabel("P(collapse)")
    ax.set_title(f"WolfGuard shifts α_c at N={N_SOCIETY}")
    ax.set_ylim(-0.05, 1.05)
    ax.grid(alpha=0.3)
    ax.legend()

    # ---------- Right panel: utility-loss vs harm-reduction tradeoff ----------
    ax2 = axes[1]
    harm_red = []
    util_loss = []
    for a in ALPHAS:
        no_def = [r for r in rows if r["alpha"] == a and r["defense"] == 0]
        wg = [r for r in rows if r["alpha"] == a and r["defense"] == 1]
        if not no_def or not wg:
            continue
        harm_red.append(np.mean([r["collapse_rate"] for r in no_def])
                        - np.mean([r["collapse_rate"] for r in wg]))
        util_loss.append(np.mean([r["utility_loss"] for r in wg]))
    ax2.scatter(util_loss, harm_red, c=ALPHAS[:len(harm_red)], cmap="viridis",
                s=80, edgecolor="k")
    for ul, hr, a in zip(util_loss, harm_red, ALPHAS):
        ax2.annotate(f"α={a:g}", (ul, hr), xytext=(5, 5),
                     textcoords="offset points", fontsize=8)
    ax2.set_xlabel("WolfGuard utility loss")
    ax2.set_ylabel("Harm reduction  (Δ P(collapse))")
    ax2.set_title("WolfGuard cost-benefit per α")
    ax2.grid(alpha=0.3)
    ax2.axhline(0, color="grey", linestyle="--", alpha=0.4)

    fig.tight_layout()
    fig.savefig(out / "defense_shift.png", dpi=140)
    plt.close(fig)

    write_json(summary, out / "summary.json")
    print(f"Done. Wrote {out}")


if __name__ == "__main__":
    main()
