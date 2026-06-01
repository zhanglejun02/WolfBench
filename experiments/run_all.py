"""Run all baseline experiments sequentially.

Usage::
    python -m experiments.run_all
"""
from __future__ import annotations

import importlib
import time

EXPERIMENTS = [
    "experiments.exp1_alpha_scaling",
    "experiments.exp2_society_size_scaling",
    "experiments.exp3_centrality_placement",
    "experiments.exp4_feedback_ablation",
    "experiments.exp5_wolfguard_defense",
    "experiments.exp6_defense_leaderboard",
]


def main():
    t_total = time.time()
    for name in EXPERIMENTS:
        print(f"\n=== {name} ===")
        t0 = time.time()
        mod = importlib.import_module(name)
        mod.main()
        print(f"  ({time.time() - t0:.1f}s)")
    print(f"\nAll experiments done in {time.time() - t_total:.1f}s")


if __name__ == "__main__":
    main()
