from experiments.defense_benchmark.exp6_defense_leaderboard import (
    _build_display_leaderboard,
)
from wolfbench.metrics import bootstrap_ci, defense_score


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
