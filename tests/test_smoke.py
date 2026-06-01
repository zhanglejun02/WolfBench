"""Smoke tests — run a tiny S0 and S1 episode end-to-end."""
import numpy as np
import pytest

from wolfbench.agents.wolfguard import WolfGuardAgent, WolfGuardConfig
from wolfbench.env.environment import WolfBenchEnv
from wolfbench.scenarios.base import load_scenario
from wolfbench.tracks.runner import calibrate_clean_baseline


@pytest.mark.parametrize("scenario", ["s0", "s1"])
def test_episode_runs(scenario):
    scen = load_scenario(scenario)
    env = WolfBenchEnv(scen, n_society=200, alpha=0.0 if scenario == "s0" else 0.05, seed=1)
    res = env.run()
    assert len(res.metrics.daily_collapse_score) == scen.horizon_days
    assert res.metrics.max_collapse_score >= 0.0


def test_pump_dump_collapse_more_likely_with_more_harmful():
    scen = load_scenario("s1")
    low = WolfBenchEnv(scen, n_society=500, alpha=0.0, seed=42).run()
    high = WolfBenchEnv(scen, n_society=500, alpha=0.10, seed=42).run()
    assert high.metrics.max_collapse_score >= low.metrics.max_collapse_score


def test_wolfguard_runs():
    scen = load_scenario("s1")
    base = calibrate_clean_baseline(n_society=200, seeds=(1, 2))
    wg = WolfGuardAgent(config=WolfGuardConfig())
    env = WolfBenchEnv(scen, n_society=300, alpha=0.05, seed=1,
                       wolfguard=wg, baseline=base)
    res = env.run()
    assert res.metrics.utility_loss >= 0.0
