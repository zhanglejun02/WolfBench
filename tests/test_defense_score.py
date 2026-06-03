from wolfbench.metrics import defense_score, bootstrap_ci


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
