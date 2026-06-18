from experiments.defense_benchmark.exp6_defense_leaderboard import (
    _build_display_leaderboard,
    _competitive_defenses,
)
import pytest

from wolfbench.metrics import bootstrap_ci, defense_score
from experiments.defense_benchmark.exp5_wolfguard_defense import summarize_threshold_shift


def _row(alpha, collapse, loss, utility=0.0, fp=0.0, cost=0.0, day=-1):
    return {
        "alpha": alpha,
        "collapse_rate": collapse,
        "collapse_day": day,
        "retail_loss_pct_30d": loss,
        "utility_loss": utility,
        "false_positive_rate": fp,
        "intervention_cost": cost,
    }


def _leaderboard_row(scenario, n_society, defense, score, shift):
    return {
        "scenario": scenario,
        "n_society": n_society,
        "defense": defense,
        "defense_score": score,
        "threshold_shift": shift,
    }


def test_harm_reduction_is_gated_without_safety_signal():
    rows_no = [_row(0.01, 1.0, 0.10), _row(0.02, 1.0, 0.10)]
    rows_def = [_row(0.01, 1.0, 0.01, utility=1.0, cost=1.0),
                _row(0.02, 1.0, 0.01, utility=1.0, cost=1.0)]
    score = defense_score(rows_no, rows_def, alphas=[0.01, 0.02])
    assert score["delta_harm_reduction"] > 0.0
    assert score["safety_gate"] == 0.0
    assert score["gated_delta_harm_reduction"] == 0.0
    assert score["defense_score"] < 0.0


def test_bootstrap_ci_singleton_is_degenerate():
    assert bootstrap_ci([3.0]) == (3.0, 3.0)


def test_negative_costs_are_not_rewards():
    rows_no = [_row(0.01, 1.0, 0.10)]
    rows_def = [_row(0.01, 1.0, 0.10, utility=-100.0, fp=2.0, cost=-100.0)]
    score = defense_score(rows_no, rows_def, alphas=[0.01])
    assert score["utility_loss"] == 0.0
    assert score["intervention_cost"] == 0.0
    assert score["false_positive_rate"] == 1.0
    assert score["defense_score"] <= 0.0


def test_exp6_display_leaderboard_aggregates_scenarios_and_sorts():
    rows = [
        _leaderboard_row("s1", 100, "alpha", 10.0, None),
        _leaderboard_row("s1", 200, "alpha", 20.0, 0.2),
        _leaderboard_row("s2", 100, "alpha", 30.0, None),
        _leaderboard_row("s3", 100, "alpha", 40.0, 0.3),
        _leaderboard_row("s4", 100, "alpha", 50.0, 0.4),
        _leaderboard_row("s1", 100, "beta", 5.0, 0.0),
        _leaderboard_row("s2", 100, "beta", 5.0, 0.0),
        _leaderboard_row("s3", 100, "beta", 5.0, 0.0),
        _leaderboard_row("s4", 100, "beta", 5.0, 0.0),
    ]

    leaderboard = _build_display_leaderboard(rows, defenses=["beta", "alpha"])

    assert [row["Defense model"] for row in leaderboard] == ["alpha", "beta"]
    alpha = leaderboard[0]
    assert alpha["S1"] == 15.0
    assert alpha["S2"] == 30.0
    assert alpha["S3"] == 40.0
    assert alpha["S4"] == 50.0
    assert alpha["Avg DefenseScore"] == 33.75
    assert alpha["Avg ThresholdShift"] == 0.2
    assert alpha["Worst Score"] == 15.0


def test_exp6_competitive_defenses_exclude_controls_and_upper_bounds():
    defenses = ["noguard", "random", "rule", "distilled", "oracle"]

    assert _competitive_defenses(defenses, upper_bounds=["oracle"]) == ["rule", "distilled"]


def test_exp6_display_leaderboard_respects_explicit_defense_filter():
    rows = [
        _leaderboard_row("s1", 1000, "noguard", 0.0, 0.0),
        _leaderboard_row("s1", 1000, "random", -1.0, 0.0),
        _leaderboard_row("s1", 1000, "rule", 2.0, 0.0),
        _leaderboard_row("s1", 1000, "distilled", 3.0, 0.0),
        _leaderboard_row("s1", 1000, "oracle", 4.0, 0.0),
    ]

    leaderboard = _build_display_leaderboard(rows, defenses=["rule", "distilled"])

    assert [row["Defense model"] for row in leaderboard] == ["distilled", "rule"]


def test_exp5_threshold_shift_summary_reports_alpha_c_delta():
    rows = []
    for alpha, no_collapse, def_collapse in [
        (0.01, 0.0, 0.0),
        (0.02, 1.0, 0.0),
        (0.03, 1.0, 1.0),
    ]:
        base = _row(alpha, no_collapse, 0.01)
        base.update({"scenario_id": "s1", "scenario": "s1", "n_society": 100, "defense": "noguard"})
        defended = _row(alpha, def_collapse, 0.005, utility=0.1, cost=0.1)
        defended.update({"scenario_id": "s1", "scenario": "s1", "n_society": 100, "defense": "rule"})
        rows.extend([base, defended])

    summary = summarize_threshold_shift(
        rows,
        defenses=["noguard", "rule"],
        scenarios=["s1"],
        n_grid=[100],
        alpha_grids={"s1": [0.01, 0.02, 0.03]},
    )

    rule = next(row for row in summary if row["defense"] == "rule")
    assert rule["alpha_c_no_def"] == 0.02
    assert rule["alpha_c_def"] == 0.03
    assert rule["threshold_shift"] == pytest.approx(0.01)
    assert rule["delta_collapse"] > 0.0
