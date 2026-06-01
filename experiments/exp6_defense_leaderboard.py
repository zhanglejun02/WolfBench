"""Exp6 — WolfBench Defense Leaderboard.

Question: when the same harmful population is held fixed, how do different
defense policies (NoGuard, RandomGuard, Rule-WolfGuard, Oracle-WolfGuard)
compare on DefenseScore + ThresholdShift?

Outputs:
* ``outputs/exp6/data.csv``       — per-(defense, scenario, alpha, seed) row
* ``outputs/exp6/leaderboard.csv``
* ``outputs/exp6/summary.json``
* ``outputs/exp6/leaderboard.png`` — DefenseScore by defense / scenario
* ``outputs/exp6/threshold_shift.png``
"""
from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from experiments._common import (
    RunSpec, exp_dir, run_grid, write_csv, write_json,
)
from wolfbench.defense import get_policy
from wolfbench.metrics import defense_score, threshold_shift
from wolfbench.tracks.runner import calibrate_clean_baseline


DEFENSES = ["noguard", "random", "rule", "oracle"]
SCENARIOS = ["s1", "s2", "s3", "s4"]
ALPHAS = [0.0, 0.005, 0.01, 0.02, 0.05, 0.1]
N_SOCIETY = 1000
SEEDS = [1, 2, 3, 4, 5]


def _build_specs(scenario: str, defense_name: str) -> list[RunSpec]:
    specs = []
    for a in ALPHAS:
        for s in SEEDS:
            policy = get_policy(defense_name)
            specs.append(RunSpec(
                scenario=scenario, n_society=N_SOCIETY, alpha=a, seed=s,
                defense=defense_name != "noguard",
                defense_policy=None if defense_name == "noguard" else policy,
                label=defense_name,
            ))
    return specs


def main():
    out = exp_dir("exp6")
    baseline = calibrate_clean_baseline(n_society=min(N_SOCIETY, 1000))

    all_rows: list[dict] = []
    for scen in SCENARIOS:
        for d in DEFENSES:
            print(f"\n=== {scen} / {d} ===")
            specs = _build_specs(scen, d)
            rows = run_grid(specs, baseline=baseline, progress_every=20)
            for r in rows:
                r["defense"] = d
                r["scenario_id"] = scen
            all_rows.extend(rows)

    write_csv(all_rows, out / "data.csv")

    # Aggregate leaderboard
    leaderboard = []
    for scen in SCENARIOS:
        rows_no = [r for r in all_rows if r["scenario_id"] == scen and r["defense"] == "noguard"]
        for d in DEFENSES:
            rows_d = [r for r in all_rows if r["scenario_id"] == scen and r["defense"] == d]
            score = defense_score(rows_no, rows_d, alphas=ALPHAS)
            shift = threshold_shift(rows_no, rows_d, ALPHAS)
            leaderboard.append({
                "scenario": scen,
                "defense": d,
                **score,
                **shift,
            })

    # Write leaderboard csv
    with open(out / "leaderboard.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(leaderboard[0].keys()))
        w.writeheader()
        for r in leaderboard:
            w.writerow(r)

    overall = []
    for d in DEFENSES:
        rows = [r for r in leaderboard if r["defense"] == d]
        overall.append({
            "defense": d,
            "defense_score_mean": float(np.mean([r["defense_score"] for r in rows])),
            "defense_score_std": float(np.std([r["defense_score"] for r in rows])),
            "threshold_shift_mean": float(np.mean([
                r["threshold_shift"] if r["threshold_shift"] is not None else 0.0
                for r in rows
            ])),
            "collapse_rate_mean": float(np.mean([r["def_collapse_rate"] for r in rows])),
            "utility_loss_mean": float(np.mean([r["utility_loss"] for r in rows])),
            "false_positive_rate_mean": float(np.mean([r["false_positive_rate"] for r in rows])),
        })

    with open(out / "leaderboard_overall.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(overall[0].keys()))
        w.writeheader()
        for r in sorted(overall, key=lambda x: x["defense_score_mean"], reverse=True):
            w.writerow(r)

    with open(out / "leaderboard.md", "w") as f:
        f.write("# WolfBench Exp6 Baseline Leaderboard\n\n")
        f.write(f"N={N_SOCIETY}, alphas={ALPHAS}, seeds={SEEDS}\n\n")
        f.write("| rank | defense | DefenseScore mean | std | mean ThresholdShift | mean CollapseRate | mean UtilityLoss | mean FP |\n")
        f.write("|---:|---|---:|---:|---:|---:|---:|---:|\n")
        for rank, r in enumerate(sorted(overall, key=lambda x: x["defense_score_mean"], reverse=True), 1):
            f.write(
                f"| {rank} | {r['defense']} | {r['defense_score_mean']:.2f} | "
                f"{r['defense_score_std']:.2f} | {r['threshold_shift_mean']:.4f} | "
                f"{r['collapse_rate_mean']:.3f} | {r['utility_loss_mean']:.3f} | "
                f"{r['false_positive_rate_mean']:.3f} |\n"
            )

    write_json({
        "defenses": DEFENSES, "scenarios": SCENARIOS,
        "alphas": ALPHAS, "n_society": N_SOCIETY, "seeds": SEEDS,
        "leaderboard": leaderboard,
        "overall": overall,
    }, out / "summary.json")

    # ---- Plot DefenseScore bars ----
    fig, ax = plt.subplots(figsize=(9, 5))
    width = 0.18
    x = np.arange(len(SCENARIOS))
    for i, d in enumerate(DEFENSES):
        vals = [next(r["defense_score"] for r in leaderboard
                     if r["scenario"] == s and r["defense"] == d)
                for s in SCENARIOS]
        ax.bar(x + (i - 1.5) * width, vals, width, label=d)
    ax.set_xticks(x)
    ax.set_xticklabels(SCENARIOS)
    ax.set_ylabel("DefenseScore")
    ax.axhline(0, color="k", lw=0.5)
    ax.set_title("WolfBench Defense Leaderboard — DefenseScore by scenario")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out / "leaderboard.png", dpi=150)
    plt.close(fig)

    # ---- Plot Threshold shift ----
    fig, ax = plt.subplots(figsize=(9, 5))
    for i, d in enumerate(DEFENSES):
        vals = [(next(r["threshold_shift"] for r in leaderboard
                      if r["scenario"] == s and r["defense"] == d) or 0.0)
                for s in SCENARIOS]
        ax.bar(x + (i - 1.5) * width, vals, width, label=d)
    ax.set_xticks(x)
    ax.set_xticklabels(SCENARIOS)
    ax.set_ylabel("ThresholdShift  Δα_c")
    ax.axhline(0, color="k", lw=0.5)
    ax.set_title("WolfBench — Critical-α shift relative to NoGuard")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out / "threshold_shift.png", dpi=150)
    plt.close(fig)

    # ---- Overall leaderboard ----
    ordered = sorted(overall, key=lambda x: x["defense_score_mean"], reverse=True)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    names = [r["defense"] for r in ordered]
    vals = [r["defense_score_mean"] for r in ordered]
    errs = [r["defense_score_std"] for r in ordered]
    ax.bar(names, vals, yerr=errs, capsize=4)
    ax.axhline(0, color="k", lw=0.5)
    ax.set_ylabel("Mean DefenseScore across S1-S4")
    ax.set_title("WolfBench Exp6 — Overall baseline leaderboard")
    fig.tight_layout()
    fig.savefig(out / "leaderboard_overall.png", dpi=150)
    plt.close(fig)

    print("\nLeaderboard written to", out)
    for r in leaderboard:
        print(f"  {r['scenario']:>3} {r['defense']:<8}  "
              f"score={r['defense_score']:>7.2f}  "
              f"Δα_c={r['threshold_shift']}")


if __name__ == "__main__":
    main()
