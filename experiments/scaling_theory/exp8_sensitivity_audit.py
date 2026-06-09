"""Experiment 8: parameter sensitivity audit.

Sweep one parameter family at a time around canonical S1-S4 settings. The
result is a robustness matrix that documents whether collapse statistics are
stable across plausible calibration ranges rather than tuned to one YAML point.

Output: outputs/scaling_theory/exp8_sensitivity_audit/
"""
from __future__ import annotations

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from experiments._common import (
    RunSpec,
    env_float_list,
    env_int_list,
    env_list,
    env_seed_list,
    run_grid,
    scaling_exp_dir,
    write_csv,
    write_json,
)
from wolfbench.metrics import binomial_rate_summary


SCENARIOS = env_list("WOLFBENCH_EXP8_SCENARIOS", "s1,s2,s3,s4")
N_SOCIETY = int(os.getenv("WOLFBENCH_EXP8_N_SOCIETY", "1000"))
SEEDS = env_seed_list("WOLFBENCH_EXP8_SEEDS", default_count=50)
DEFAULT_ALPHAS = {
    "s1": 0.015,
    "s2": 0.001,
    "s3": 0.35,
    "s4": 0.03,
}


def _alpha_for(scenario: str) -> float:
    return float(os.getenv(f"WOLFBENCH_EXP8_ALPHA_{scenario.upper()}", DEFAULT_ALPHAS[scenario]))


def _spec_for(scenario: str, seed: int, family: str, value: float | int | str) -> RunSpec:
    alpha = _alpha_for(scenario)
    if family == "feedback_strength":
        return RunSpec(scenario, N_SOCIETY, alpha, seed, feedback_strength=float(value), label=f"{family}={value}")
    if family == "asset_liquidity_scale":
        return RunSpec(scenario, N_SOCIETY, alpha, seed, asset_liquidity_scale=float(value), label=f"{family}={value}")
    if family == "retail_wealth_scale":
        return RunSpec(scenario, N_SOCIETY, alpha, seed, retail_wealth_scale=float(value), label=f"{family}={value}")
    if family == "retail_risk_appetite":
        return RunSpec(scenario, N_SOCIETY, alpha, seed, retail_risk_appetite=float(value), label=f"{family}={value}")
    if family == "social_mean_degree":
        return RunSpec(scenario, N_SOCIETY, alpha, seed, social_mean_degree=int(value), label=f"{family}={value}")
    if family == "placement":
        return RunSpec(scenario, N_SOCIETY, alpha, seed, placement=str(value), label=f"{family}={value}")
    raise ValueError(f"Unknown sensitivity family: {family}")


def _parameter_grid() -> dict[str, list[float | int | str]]:
    return {
        "feedback_strength": env_float_list("WOLFBENCH_EXP8_FEEDBACKS", "0.0,0.4,0.8,1.2,1.6"),
        "asset_liquidity_scale": env_float_list("WOLFBENCH_EXP8_LIQUIDITY_SCALES", "0.5,0.75,1.0,1.5,2.0"),
        "retail_wealth_scale": env_float_list("WOLFBENCH_EXP8_WEALTH_SCALES", "0.5,1.0,2.0"),
        "retail_risk_appetite": env_float_list("WOLFBENCH_EXP8_RISK_APPETITES", "0.01,0.02,0.04"),
        "social_mean_degree": env_int_list("WOLFBENCH_EXP8_MEAN_DEGREES", "4,8,12,16"),
        "placement": env_list("WOLFBENCH_EXP8_PLACEMENTS", "random,high_degree"),
    }


def main() -> None:
    out = scaling_exp_dir("exp8_sensitivity_audit")
    grid = _parameter_grid()
    specs = []
    for scenario in SCENARIOS:
        for family, values in grid.items():
            for value in values:
                for seed in SEEDS:
                    specs.append(_spec_for(scenario, seed, family, value))

    print(f"Running {len(specs)} episodes for exp8...")
    rows = run_grid(specs)
    write_csv(rows, out / "data.csv")

    summary_rows = []
    metrics = ["collapse_rate", "max_collapse_score", "retail_loss_pct_30d", "price_dislocation_max"]
    for scenario in SCENARIOS:
        for family, values in grid.items():
            for value in values:
                selected = [
                    r for r in rows
                    if r["scenario"] == scenario and r["label"] == f"{family}={value}"
                ]
                row = {
                    "scenario": scenario,
                    "alpha": _alpha_for(scenario),
                    "n_society": N_SOCIETY,
                    "family": family,
                    "value": value,
                    "n": len(selected),
                }
                for metric in metrics:
                    vals = np.array([float(r[metric]) for r in selected], dtype=float)
                    row[f"{metric}_mean"] = float(vals.mean()) if vals.size else 0.0
                    row[f"{metric}_std"] = float(vals.std()) if vals.size else 0.0
                    if metric == "collapse_rate":
                        ci = binomial_rate_summary(vals)
                        row["collapse_rate_ci_low"] = ci["ci_low"]
                        row["collapse_rate_ci_high"] = ci["ci_high"]
                        row["collapse_successes"] = ci["successes"]
                summary_rows.append(row)
    write_csv(summary_rows, out / "sensitivity_summary.csv")

    fig, axes = plt.subplots(len(SCENARIOS), 1, figsize=(9, 3.2 * len(SCENARIOS)), sharex=False)
    if len(SCENARIOS) == 1:
        axes = [axes]
    for ax, scenario in zip(axes, SCENARIOS):
        plot_rows = [r for r in summary_rows if r["scenario"] == scenario and r["family"] == "feedback_strength"]
        xs = [float(r["value"]) for r in plot_rows]
        ys = [float(r["collapse_rate_mean"]) for r in plot_rows]
        yerr = [
            [max(0.0, y - float(r["collapse_rate_ci_low"])) for y, r in zip(ys, plot_rows)],
            [max(0.0, float(r["collapse_rate_ci_high"]) - y) for y, r in zip(ys, plot_rows)],
        ]
        ax.errorbar(xs, ys, yerr=yerr, marker="o", capsize=4)
        ax.set_title(f"{scenario.upper()} feedback sensitivity")
        ax.set_ylabel("P(collapse)")
        ax.grid(alpha=0.3)
    axes[-1].set_xlabel("social.feedback_strength")
    fig.tight_layout()
    fig.savefig(out / "feedback_sensitivity.png", dpi=150)
    plt.close(fig)

    write_json({
        "scenarios": SCENARIOS,
        "n_society": N_SOCIETY,
        "alphas": {scenario: _alpha_for(scenario) for scenario in SCENARIOS},
        "seeds": SEEDS,
        "parameter_grid": grid,
        "summary_csv": "sensitivity_summary.csv",
    }, out / "summary.json")
    print(f"Done. Wrote {out}")


if __name__ == "__main__":
    main()