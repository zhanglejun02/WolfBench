"""Exp6 — WolfBench Defense Leaderboard.

Question: when the same harmful population is held fixed, how do different
defense policies compare on DefenseScore + ThresholdShift?

Outputs:
* ``outputs/exp6/data.csv``       — per-(defense, scenario, alpha, seed) row
* ``outputs/exp6/leaderboard.csv``
* ``outputs/exp6/summary.json``
* ``outputs/exp6/leaderboard.png`` — DefenseScore by defense / scenario
* ``outputs/exp6/threshold_shift.png``
"""
from __future__ import annotations

import csv
import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from experiments._common import (
    RunSpec, exp_dir, run_grid, write_csv, write_json,
)
from wolfbench.defense import get_policy, get_track
from wolfbench.metrics import bootstrap_ci, defense_score, threshold_shift
from wolfbench.tracks.runner import calibrate_clean_baseline


def _env_list(name: str, default: str) -> list[str]:
    return [x.strip() for x in os.getenv(name, default).split(",") if x.strip()]


def _env_float_list(name: str, default: str) -> list[float]:
    return [float(x) for x in _env_list(name, default)]


def _env_int_list(name: str, default: str) -> list[int]:
    return [int(x) for x in _env_list(name, default)]


ELIGIBLE_DEFENSES = _env_list("WOLFBENCH_EXP6_DEFENSES", "noguard,random,rule")
UPPER_BOUNDS = _env_list("WOLFBENCH_EXP6_UPPER_BOUNDS", "oracle")
DEFENSES = ELIGIBLE_DEFENSES + UPPER_BOUNDS
SCENARIOS = _env_list("WOLFBENCH_EXP6_SCENARIOS", "s1,s2,s3,s4")
DEFAULT_ALPHA_GRIDS = {
    "s1": "0.0,0.0075,0.01,0.015,0.02,0.03",
    "s2": "0.0,0.00025,0.0005,0.00075,0.001,0.0015,0.0025",
    "s3": "0.0,0.15,0.3,0.4,0.5",
    "s4": "0.0,0.01,0.015,0.02,0.03,0.05,0.1,0.15,0.2",
}
GLOBAL_ALPHAS = os.getenv("WOLFBENCH_EXP6_ALPHAS")
N_GRID = _env_int_list("WOLFBENCH_EXP6_N_GRID", os.getenv("WOLFBENCH_EXP6_N_SOCIETY", "500,1000,2000"))
SEEDS = _env_int_list("WOLFBENCH_EXP6_SEEDS", "1,2,3,4,5")
CI_BOOT = int(os.getenv("WOLFBENCH_EXP6_CI_BOOT", "2000"))
OUT_NAME = os.getenv("WOLFBENCH_EXP6_OUT", "exp6")


def _alphas_for(scenario: str) -> list[float]:
    key = f"WOLFBENCH_EXP6_ALPHAS_{scenario.upper()}"
    default = GLOBAL_ALPHAS or DEFAULT_ALPHA_GRIDS.get(scenario, "0.0,0.005,0.01,0.02,0.05,0.1")
    return _env_float_list(key, default)


def _build_specs(scenario: str, defense_name: str, n_society: int) -> list[RunSpec]:
    specs = []
    for a in _alphas_for(scenario):
        for s in SEEDS:
            policy = get_policy(defense_name)
            specs.append(RunSpec(
                scenario=scenario, n_society=n_society, alpha=a, seed=s,
                defense=defense_name != "noguard",
                defense_policy=None if defense_name == "noguard" else policy,
                label=defense_name,
            ))
    return specs


def _official_score(defense_name: str, raw_score: float) -> float:
    if get_track(defense_name) == "control":
        return min(float(raw_score), 0.0)
    return float(raw_score)


def main():
    out = exp_dir(OUT_NAME)
    alpha_grids = {s: _alphas_for(s) for s in SCENARIOS}
    baseline = calibrate_clean_baseline(n_society=min(max(N_GRID), 1000))

    all_rows: list[dict] = []
    for scen in SCENARIOS:
        for n_society in N_GRID:
            for d in DEFENSES:
                print(f"\n=== {scen} / N={n_society} / {d} ===")
                specs = _build_specs(scen, d, n_society)
                rows = run_grid(specs, baseline=baseline, progress_every=20)
                for r in rows:
                    r["defense"] = d
                    r["track"] = get_track(d)
                    r["scenario_id"] = scen
                all_rows.extend(rows)

    write_csv(all_rows, out / "data.csv")

    # Aggregate leaderboard
    leaderboard = []
    for scen in SCENARIOS:
        alphas = _alphas_for(scen)
        for n_society in N_GRID:
            rows_no = [r for r in all_rows if r["scenario_id"] == scen
                       and int(r["n_society"]) == n_society and r["defense"] == "noguard"]
            for d in DEFENSES:
                rows_d = [r for r in all_rows if r["scenario_id"] == scen
                          and int(r["n_society"]) == n_society and r["defense"] == d]
                score = defense_score(rows_no, rows_d, alphas=alphas)
                shift = threshold_shift(rows_no, rows_d, alphas)
                leaderboard.append({
                    "scenario": scen,
                    "n_society": n_society,
                    "defense": d,
                    "track": get_track(d),
                    "eligible": d in ELIGIBLE_DEFENSES,
                    "official_score": _official_score(d, score["defense_score"]),
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
        scores = [r["defense_score"] for r in rows]
        official_scores = [r["official_score"] for r in rows]
        ci_low, ci_high = bootstrap_ci(scores, n_boot=CI_BOOT)
        official_ci_low, official_ci_high = bootstrap_ci(official_scores, n_boot=CI_BOOT)
        overall.append({
            "defense": d,
            "track": get_track(d),
            "eligible": d in ELIGIBLE_DEFENSES,
            "official_score_mean": float(np.mean(official_scores)),
            "official_score_ci_low": official_ci_low,
            "official_score_ci_high": official_ci_high,
            "defense_score_mean": float(np.mean(scores)),
            "defense_score_std": float(np.std(scores)),
            "defense_score_ci_low": ci_low,
            "defense_score_ci_high": ci_high,
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
        for r in sorted(overall, key=lambda x: x["official_score_mean"], reverse=True):
            w.writerow(r)

    with open(out / "leaderboard.md", "w") as f:
        f.write("# WolfBench Exp6 Baseline Leaderboard\n\n")
        f.write(f"N={N_GRID}, alpha_grids={alpha_grids}, seeds={SEEDS}\n\n")
        f.write("Control tracks are diagnostic only: their official score is capped at 0 while raw DefenseScore is still reported. Oracle upper bounds are listed separately and are not eligible for the competitive leaderboard.\n\n")
        f.write("## Eligible defenses\n\n")
        f.write("| rank | track | defense | OfficialScore mean | 95% CI | raw DefenseScore mean | raw 95% CI | mean ThresholdShift | mean CollapseRate | mean UtilityLoss | mean FP |\n")
        f.write("|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|\n")
        eligible_rows = [r for r in overall if r["eligible"]]
        for rank, r in enumerate(sorted(eligible_rows, key=lambda x: x["official_score_mean"], reverse=True), 1):
            f.write(
                f"| {rank} | {r['track']} | {r['defense']} | {r['official_score_mean']:.2f} | "
                f"[{r['official_score_ci_low']:.2f}, {r['official_score_ci_high']:.2f}] | "
                f"{r['defense_score_mean']:.2f} | "
                f"[{r['defense_score_ci_low']:.2f}, {r['defense_score_ci_high']:.2f}] | "
                f"{r['threshold_shift_mean']:.4f} | "
                f"{r['collapse_rate_mean']:.3f} | {r['utility_loss_mean']:.3f} | "
                f"{r['false_positive_rate_mean']:.3f} |\n"
            )
        upper_rows = [r for r in overall if not r["eligible"]]
        if upper_rows:
            f.write("\n## Upper bounds\n\n")
            f.write("| track | defense | OfficialScore mean | raw DefenseScore mean | mean ThresholdShift |\n")
            f.write("|---|---|---:|---:|---:|\n")
            for r in sorted(upper_rows, key=lambda x: x["official_score_mean"], reverse=True):
                f.write(
                    f"| {r['track']} | {r['defense']} | {r['official_score_mean']:.2f} | "
                    f"{r['defense_score_mean']:.2f} | {r['threshold_shift_mean']:.4f} |\n"
                )

    write_json({
        "eligible_defenses": ELIGIBLE_DEFENSES,
        "upper_bounds": UPPER_BOUNDS,
        "defenses": DEFENSES, "scenarios": SCENARIOS,
        "alpha_grids": alpha_grids,
        "n_grid": N_GRID, "seeds": SEEDS,
        "leaderboard": leaderboard,
        "overall": overall,
    }, out / "summary.json")

    # ---- Plot DefenseScore bars ----
    fig, ax = plt.subplots(figsize=(9, 5))
    width = min(0.8 / max(len(DEFENSES), 1), 0.18)
    xlabels = [f"{s}\nN={n}" for s in SCENARIOS for n in N_GRID]
    x = np.arange(len(xlabels))
    for i, d in enumerate(DEFENSES):
        vals = [next(r["defense_score"] for r in leaderboard
                     if r["scenario"] == s and r["n_society"] == n and r["defense"] == d)
                for s in SCENARIOS for n in N_GRID]
        ax.bar(x + (i - (len(DEFENSES) - 1) / 2) * width, vals, width, label=d)
    ax.set_xticks(x)
    ax.set_xticklabels(xlabels, rotation=45, ha="right")
    ax.set_ylabel("Raw DefenseScore")
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
                      if r["scenario"] == s and r["n_society"] == n and r["defense"] == d) or 0.0)
                for s in SCENARIOS for n in N_GRID]
        ax.bar(x + (i - (len(DEFENSES) - 1) / 2) * width, vals, width, label=d)
    ax.set_xticks(x)
    ax.set_xticklabels(xlabels, rotation=45, ha="right")
    ax.set_ylabel("ThresholdShift  Δα_c")
    ax.axhline(0, color="k", lw=0.5)
    ax.set_title("WolfBench — Critical-α shift relative to NoGuard")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out / "threshold_shift.png", dpi=150)
    plt.close(fig)

    # ---- Overall leaderboard ----
    ordered = sorted(overall, key=lambda x: x["official_score_mean"], reverse=True)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    names = [r["defense"] for r in ordered]
    vals = [r["official_score_mean"] for r in ordered]
    yerr = [
        [r["official_score_mean"] - r["official_score_ci_low"] for r in ordered],
        [r["official_score_ci_high"] - r["official_score_mean"] for r in ordered],
    ]
    ax.bar(names, vals, yerr=yerr, capsize=4)
    ax.axhline(0, color="k", lw=0.5)
    ax.set_ylabel("Mean OfficialScore across S1-S4")
    ax.set_title("WolfBench Exp6 — Overall baseline leaderboard")
    fig.tight_layout()
    fig.savefig(out / "leaderboard_overall.png", dpi=150)
    plt.close(fig)

    print("\nLeaderboard written to", out)
    for r in leaderboard:
          print(f"  {r['scenario']:>3} {r['defense']:<8}  "
              f"N={r['n_society']:<5} score={r['defense_score']:>7.2f}  "
              f"Δα_c={r['threshold_shift']}")


if __name__ == "__main__":
    main()
