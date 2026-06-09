"""Exp6 — WolfBench Defense Leaderboard.

Question: when the same harmful population is held fixed, how do different
defense policies compare on DefenseScore + ThresholdShift?

Outputs:
* ``outputs/defense_benchmark/exp6/data.csv``       — per-(defense, scenario, alpha, seed) row
* ``outputs/defense_benchmark/exp6/leaderboard_by_scenario.csv`` — per-scenario/N aggregate
* ``outputs/defense_benchmark/exp6/leaderboard.csv`` — display leaderboard
* ``outputs/defense_benchmark/exp6/leaderboard_overall.csv`` — display leaderboard alias
* ``outputs/defense_benchmark/exp6/summary.json``
* ``outputs/defense_benchmark/exp6/leaderboard.png`` — DefenseScore by defense / scenario
* ``outputs/defense_benchmark/exp6/threshold_shift.png``
"""
from __future__ import annotations

import csv
import os

import matplotlib.pyplot as plt
import numpy as np

from experiments._common import (
    RunSpec, benchmark_exp_dir, run_grid, write_csv, write_json,
)
from wolfbench.defense import get_policy, get_track
from wolfbench.metrics import bootstrap_ci, defense_score, rank_stability, threshold_shift
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
SEEDS = _env_int_list(
    "WOLFBENCH_EXP6_SEEDS",
    ",".join(str(i) for i in range(1, 31)),
)
CI_BOOT = int(os.getenv("WOLFBENCH_EXP6_CI_BOOT", "2000"))
OUT_NAME = os.getenv("WOLFBENCH_EXP6_OUT", "exp6")
DISPLAY_SCENARIOS = ("s1", "s2", "s3", "s4")
DISPLAY_FIELDNAMES = [
    "Defense model", "S1", "S2", "S3", "S4",
    "Avg DefenseScore", "Avg ThresholdShift", "Worst Score",
]


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


def _to_float(value, default: float = 0.0) -> float:
    if value is None:
        return default
    if isinstance(value, str) and value.strip() in {"", "None", "none", "null", "nan"}:
        return default
    return float(value)


def _mean(values: list[float]) -> float:
    return float(np.mean(values)) if values else 0.0


def _defenses_in_order(rows: list[dict], defenses: list[str] | None = None) -> list[str]:
    row_defenses = {str(r.get("defense", r.get("Defense model", ""))) for r in rows}
    ordered: list[str] = []
    for defense_name in defenses or []:
        if defense_name in row_defenses and defense_name not in ordered:
            ordered.append(defense_name)
    for row in rows:
        defense_name = str(row.get("defense", row.get("Defense model", "")))
        if defense_name and defense_name not in ordered:
            ordered.append(defense_name)
    return ordered


def _build_display_leaderboard(
    scenario_leaderboard: list[dict],
    defenses: list[str] | None = None,
    scenarios: tuple[str, ...] = DISPLAY_SCENARIOS,
) -> list[dict]:
    """Build the public S1-S4 defense leaderboard from per-scenario rows."""
    by_defense_scenario: dict[tuple[str, str], list[dict]] = {}
    for row in scenario_leaderboard:
        defense_name = str(row.get("defense", row.get("Defense model", "")))
        scenario = str(row.get("scenario", "")).lower()
        if defense_name and scenario in scenarios:
            by_defense_scenario.setdefault((defense_name, scenario), []).append(row)

    display_rows: list[dict] = []
    for defense_name in _defenses_in_order(scenario_leaderboard, defenses):
        scenario_scores: dict[str, float | None] = {}
        scenario_shifts: list[float] = []
        for scenario in scenarios:
            rows = by_defense_scenario.get((defense_name, scenario), [])
            if rows:
                scenario_scores[scenario] = _mean([
                    _to_float(r.get("defense_score")) for r in rows
                ])
                scenario_shifts.append(_mean([
                    _to_float(r.get("threshold_shift"), default=0.0) for r in rows
                ]))
            else:
                scenario_scores[scenario] = None

        available_scores = [v for v in scenario_scores.values() if v is not None]
        display_row = {
            "Defense model": defense_name,
            "S1": scenario_scores["s1"] if scenario_scores["s1"] is not None else "",
            "S2": scenario_scores["s2"] if scenario_scores["s2"] is not None else "",
            "S3": scenario_scores["s3"] if scenario_scores["s3"] is not None else "",
            "S4": scenario_scores["s4"] if scenario_scores["s4"] is not None else "",
            "Avg DefenseScore": _mean(available_scores),
            "Avg ThresholdShift": _mean(scenario_shifts),
            "Worst Score": min(available_scores) if available_scores else 0.0,
        }
        display_rows.append(display_row)

    display_rows.sort(key=lambda r: _to_float(r["Avg DefenseScore"]), reverse=True)
    return display_rows


def _write_display_csv(rows: list[dict], path) -> None:
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=DISPLAY_FIELDNAMES)
        w.writeheader()
        for row in rows:
            w.writerow(row)


def _format_score(value) -> str:
    if value == "" or value is None:
        return ""
    return f"{float(value):.2f}"


def _format_shift(value) -> str:
    return f"{_to_float(value):.4f}"


def _scenario_metric_means(
    scenario_leaderboard: list[dict],
    defense_name: str,
    metric: str,
    scenarios: tuple[str, ...] = DISPLAY_SCENARIOS,
    none_as_zero: bool = False,
) -> list[float]:
    vals: list[float] = []
    for scenario in scenarios:
        rows = [
            r for r in scenario_leaderboard
            if str(r.get("defense")) == defense_name and str(r.get("scenario", "")).lower() == scenario
        ]
        default = 0.0 if none_as_zero else float("nan")
        metric_vals = [_to_float(r.get(metric), default=default) for r in rows]
        if metric_vals:
            vals.append(_mean(metric_vals))
        else:
            vals.append(0.0)
    return vals


def _seed_level_rank_rows(all_rows: list[dict]) -> list[dict]:
    """Per-seed score rows used to estimate leaderboard rank stability."""
    rank_rows: list[dict] = []
    seeds = sorted({int(r["seed"]) for r in all_rows})
    scenarios = sorted({str(r["scenario_id"]) for r in all_rows})
    n_values = sorted({int(r["n_society"]) for r in all_rows})
    for seed in seeds:
        for defense_name in DEFENSES:
            scores = []
            official_scores = []
            for scenario in scenarios:
                alphas = _alphas_for(scenario)
                for n_society in n_values:
                    rows_no = [
                        r for r in all_rows
                        if int(r["seed"]) == seed
                        and str(r["scenario_id"]) == scenario
                        and int(r["n_society"]) == n_society
                        and r["defense"] == "noguard"
                    ]
                    rows_def = [
                        r for r in all_rows
                        if int(r["seed"]) == seed
                        and str(r["scenario_id"]) == scenario
                        and int(r["n_society"]) == n_society
                        and r["defense"] == defense_name
                    ]
                    if not rows_no or not rows_def:
                        continue
                    score = defense_score(rows_no, rows_def, alphas=alphas)["defense_score"]
                    scores.append(score)
                    official_scores.append(_official_score(defense_name, score))
            if scores:
                rank_rows.append({
                    "seed": seed,
                    "defense": defense_name,
                    "defense_score": float(np.mean(scores)),
                    "official_score": float(np.mean(official_scores)),
                })
    return rank_rows


def main():
    out = benchmark_exp_dir(OUT_NAME)
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

    # Aggregate per-scenario leaderboard rows. These preserve the raw metric
    # components used by summary.json and downstream analysis.
    scenario_leaderboard = []
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
                scenario_leaderboard.append({
                    "scenario": scen,
                    "n_society": n_society,
                    "defense": d,
                    "track": get_track(d),
                    "eligible": d in ELIGIBLE_DEFENSES,
                    "official_score": _official_score(d, score["defense_score"]),
                    **score,
                    **shift,
                })

    with open(out / "leaderboard_by_scenario.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(scenario_leaderboard[0].keys()))
        w.writeheader()
        for r in scenario_leaderboard:
            w.writerow(r)

    display_leaderboard = _build_display_leaderboard(scenario_leaderboard, DEFENSES)
    _write_display_csv(display_leaderboard, out / "leaderboard.csv")
    _write_display_csv(display_leaderboard, out / "leaderboard_overall.csv")

    overall_metrics = []
    seed_rank_rows = _seed_level_rank_rows(all_rows)
    rank_stability_summary = rank_stability(
        seed_rank_rows,
        score_key="official_score",
        item_key="defense",
        sample_key="seed",
        n_boot=CI_BOOT,
        top_k=min(3, len(DEFENSES)),
        seed=17,
    )
    for d in DEFENSES:
        rows = [r for r in scenario_leaderboard if r["defense"] == d]
        scores = [r["defense_score"] for r in rows]
        official_scores = [r["official_score"] for r in rows]
        ci_low, ci_high = bootstrap_ci(scores, n_boot=CI_BOOT)
        official_ci_low, official_ci_high = bootstrap_ci(official_scores, n_boot=CI_BOOT)
        overall_metrics.append({
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

    with open(out / "leaderboard.md", "w") as f:
        f.write("# WolfBench Exp6 Defense Leaderboard\n\n")
        f.write(f"N={N_GRID}, alpha_grids={alpha_grids}, seeds={SEEDS}\n\n")
        f.write("S1-S4 are mean raw DefenseScore values for each scenario, averaged across N. Avg ThresholdShift treats missing per-scenario threshold_shift values as 0.0.\n\n")
        f.write("| Defense model | S1 | S2 | S3 | S4 | Avg DefenseScore | Avg ThresholdShift | Worst Score |\n")
        f.write("|---|---:|---:|---:|---:|---:|---:|---:|\n")
        for r in display_leaderboard:
            f.write(
                f"| {r['Defense model']} | {_format_score(r['S1'])} | {_format_score(r['S2'])} | "
                f"{_format_score(r['S3'])} | {_format_score(r['S4'])} | "
                f"{_format_score(r['Avg DefenseScore'])} | {_format_shift(r['Avg ThresholdShift'])} | "
                f"{_format_score(r['Worst Score'])} |\n"
            )

    write_json({
        "eligible_defenses": ELIGIBLE_DEFENSES,
        "upper_bounds": UPPER_BOUNDS,
        "defenses": DEFENSES, "scenarios": SCENARIOS,
        "alpha_grids": alpha_grids,
        "n_grid": N_GRID, "seeds": SEEDS,
        "leaderboard": scenario_leaderboard,
        "overall": overall_metrics,
        "display_leaderboard": display_leaderboard,
        "seed_rank_stability": rank_stability_summary,
        "seed_level_rank_rows": seed_rank_rows,
    }, out / "summary.json")

    # ---- Plot DefenseScore bars ----
    fig, ax = plt.subplots(figsize=(9, 5))
    ordered_defenses = [r["Defense model"] for r in display_leaderboard]
    width = min(0.8 / max(len(ordered_defenses), 1), 0.18)
    xlabels = [s.upper() for s in DISPLAY_SCENARIOS]
    x = np.arange(len(xlabels))
    for i, d in enumerate(ordered_defenses):
        vals = _scenario_metric_means(scenario_leaderboard, d, "defense_score")
        ax.bar(x + (i - (len(ordered_defenses) - 1) / 2) * width, vals, width, label=d)
    ax.set_xticks(x)
    ax.set_xticklabels(xlabels)
    ax.set_ylabel("Raw DefenseScore")
    ax.axhline(0, color="k", lw=0.5)
    ax.set_title("WolfBench Defense Leaderboard — DefenseScore by scenario")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out / "leaderboard.png", dpi=150)
    plt.close(fig)

    # ---- Plot Threshold shift ----
    fig, ax = plt.subplots(figsize=(9, 5))
    for i, d in enumerate(ordered_defenses):
        vals = _scenario_metric_means(scenario_leaderboard, d, "threshold_shift", none_as_zero=True)
        ax.bar(x + (i - (len(ordered_defenses) - 1) / 2) * width, vals, width, label=d)
    ax.set_xticks(x)
    ax.set_xticklabels(xlabels)
    ax.set_ylabel("ThresholdShift  Δα_c")
    ax.axhline(0, color="k", lw=0.5)
    ax.set_title("WolfBench — Critical-α shift relative to NoGuard")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out / "threshold_shift.png", dpi=150)
    plt.close(fig)

    # ---- Overall leaderboard ----
    fig, ax = plt.subplots(figsize=(8, 4.5))
    names = [r["Defense model"] for r in display_leaderboard]
    vals = [r["Avg DefenseScore"] for r in display_leaderboard]
    ax.bar(names, vals)
    ax.axhline(0, color="k", lw=0.5)
    ax.set_ylabel("Avg DefenseScore across S1-S4")
    ax.set_title("WolfBench Exp6 — Overall defense leaderboard")
    fig.tight_layout()
    fig.savefig(out / "leaderboard_overall.png", dpi=150)
    plt.close(fig)

    print("\nLeaderboard written to", out)
    for r in display_leaderboard:
        print(
            f"  {r['Defense model']:<12} avg={r['Avg DefenseScore']:>7.2f}  "
            f"worst={r['Worst Score']:>7.2f}  Δα_c_avg={r['Avg ThresholdShift']}"
        )


if __name__ == "__main__":
    main()
