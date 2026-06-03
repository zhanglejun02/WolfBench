"""Shared helpers for WolfBench experiments.

Scaling-theory experiments write to ``outputs/scaling_theory/<exp_name>/``.
Defense-benchmark experiments write to ``outputs/defense_benchmark/<exp_name>/``.
Each experiment directory contains at least:
* ``config.json``  -- experiment configuration
* ``data.csv``     -- raw per-episode metrics
* one or more ``*.png`` figures

Use :func:`run_grid` for a uniform episode sweep.
"""
from __future__ import annotations

import csv
import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import numpy as np

from wolfbench.agents.wolfguard import WolfGuardAgent, WolfGuardConfig
from wolfbench.env.environment import WolfBenchEnv
from wolfbench.scenarios.base import load_scenario
from wolfbench.tracks.runner import calibrate_clean_baseline


REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUTS_ROOT = REPO_ROOT / "outputs"
SCALING_THEORY_OUTPUTS_ROOT = OUTPUTS_ROOT / "scaling_theory"
DEFENSE_BENCHMARK_OUTPUTS_ROOT = OUTPUTS_ROOT / "defense_benchmark"


def exp_dir(name: str, track: str | None = None) -> Path:
    root = OUTPUTS_ROOT if track is None else OUTPUTS_ROOT / track
    d = root / name
    d.mkdir(parents=True, exist_ok=True)
    return d


def scaling_exp_dir(name: str) -> Path:
    return exp_dir(name, "scaling_theory")


def benchmark_exp_dir(name: str) -> Path:
    return exp_dir(name, "defense_benchmark")


@dataclass
class RunSpec:
    scenario: str
    n_society: int
    alpha: float
    seed: int
    placement: str | None = None
    feedback_strength: float | None = None   # mutate scenario.social
    defense: bool = False
    defense_mode: str = "full"
    defense_policy: Any = None                # WolfGuardPolicy override
    label: str = ""                          # tag for plotting


def run_episode(spec: RunSpec, baseline=None) -> dict[str, Any]:
    scen = load_scenario(spec.scenario)
    if spec.feedback_strength is not None:
        scen.social["feedback_strength"] = float(spec.feedback_strength)

    wg = None
    if spec.defense_policy is not None:
        wg = spec.defense_policy
        if hasattr(wg, "fit_baseline") and baseline is not None:
            wg.fit_baseline(baseline)
    elif spec.defense:
        wg = WolfGuardAgent(config=WolfGuardConfig(mode=spec.defense_mode))

    env = WolfBenchEnv(
        scen, n_society=spec.n_society, alpha=spec.alpha, seed=spec.seed,
        wolfguard=wg, baseline=baseline,
        placement_override=spec.placement,
        expose_oracle=(spec.label == "oracle" or wg.__class__.__name__ == "OracleWolfGuardPolicy" if wg is not None else False),
    )
    res = env.run()
    m = res.metrics
    return {
        "scenario": spec.scenario,
        "n_society": spec.n_society,
        "alpha": spec.alpha,
        "seed": spec.seed,
        "placement": spec.placement or "",
        "feedback_strength": (
            float(spec.feedback_strength) if spec.feedback_strength is not None else float("nan")
        ),
        "defense": int(spec.defense),
        "defense_mode": spec.defense_mode if spec.defense else "",
        "label": spec.label,
        "collapse_rate": m.collapse_rate,
        "collapse_day": m.collapse_day if m.collapse_day is not None else -1,
        "max_collapse_score": m.max_collapse_score,
        "retail_loss_pct_30d": m.retail_loss_pct_30d,
        "harmful_profit": m.harmful_profit,
        "wealth_transfer": m.wealth_transfer,
        "price_dislocation_max": m.price_dislocation_max,
        "liquidity_stress_max": m.liquidity_stress_max,
        "social_cascade_peak": m.social_cascade_peak,
        "intervention_cost": m.intervention_cost,
        "utility_loss": m.utility_loss,
        "false_positive_rate": m.false_positive_rate,
    }


def run_grid(specs: Iterable[RunSpec], baseline=None,
             progress_every: int = 10) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    specs = list(specs)
    t0 = time.time()
    for i, s in enumerate(specs, 1):
        rows.append(run_episode(s, baseline=baseline))
        if i % progress_every == 0 or i == len(specs):
            dt = time.time() - t0
            print(f"[{i:>4}/{len(specs)}] {dt:6.1f}s elapsed", flush=True)
    return rows


def write_csv(rows: list[dict[str, Any]], path: Path) -> None:
    if not rows:
        return
    keys = list(rows[0].keys())
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def write_json(obj: Any, path: Path) -> None:
    with open(path, "w") as f:
        json.dump(obj, f, indent=2, default=str)


def aggregate(rows: list[dict[str, Any]], group_by: list[str], metric: str
              ) -> dict[tuple, dict[str, float]]:
    """Return mean/std/n per (group key tuple)."""
    buckets: dict[tuple, list[float]] = {}
    for r in rows:
        key = tuple(r[g] for g in group_by)
        buckets.setdefault(key, []).append(float(r[metric]))
    out: dict[tuple, dict[str, float]] = {}
    for k, vals in buckets.items():
        a = np.array(vals)
        out[k] = {"mean": float(a.mean()), "std": float(a.std()),
                  "n": int(a.size), "values": vals}
    return out


def alpha_critical(rows: list[dict[str, Any]], alphas: list[float],
                   n_society: int, threshold: float = 0.5) -> float | None:
    by_alpha = aggregate([r for r in rows if r["n_society"] == n_society],
                         ["alpha"], "collapse_rate")
    for a in sorted(alphas):
        m = by_alpha.get((a,), {}).get("mean", 0.0)
        if m >= threshold:
            return float(a)
    return None
