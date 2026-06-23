from experiments.defense_benchmark.exp6_defense_leaderboard import (
    _build_display_leaderboard,
    _competitive_defenses,
)
import pytest

from wolfbench.metrics import bootstrap_ci, defense_score, threshold_protection_score
from experiments.defense_benchmark.exp5_wolfguard_defense import summarize_threshold_shift
from experiments.defense_benchmark.exp7_threshold_shift_defense import _main_table
from experiments.scaling_theory.exp10_comparative_statics_threshold import _delta_rows
from experiments.scaling_theory.exp8_sensitivity_audit import _alpha_c_rows, _family_delta_rows


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
        "track": "submission",
        "tps": score,
        "tps_official": score,
        "delta_alpha_c_over_w0": shift or 0.0,
        "critical_band_delta_p": 0.1,
        "clean_cost_index": 0.01,
        "clean_false_positive_rate": 0.02,
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

    assert [row["Defense"] for row in leaderboard] == ["alpha", "beta"]
    alpha = leaderboard[0]
    assert alpha["TPS"] == 33.75
    assert alpha["DeltaAlphaC/W0"] == 0.2
    assert alpha["CriticalDeltaP"] == 0.1
    assert alpha["CleanCost"] == 0.01
    assert alpha["FP"] == 0.02


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

    assert [row["Defense"] for row in leaderboard] == ["distilled", "rule"]


def test_tps_is_nonnegative_and_rewards_threshold_shift():
    rows_no = []
    rows_def = []
    for alpha, no_collapse, def_collapse in [
        (0.0, 0.0, 0.0),
        (0.01, 0.0, 0.0),
        (0.02, 1.0, 0.0),
        (0.03, 1.0, 1.0),
    ]:
        rows_no.append(_row(alpha, no_collapse, 0.10, utility=0.0, fp=0.0, cost=0.0))
        rows_def.append(_row(alpha, def_collapse, 0.05, utility=0.0, fp=0.0, cost=0.0))

    score = threshold_protection_score(rows_no, rows_def, alphas=[0.0, 0.01, 0.02, 0.03])

    assert score["tps"] > 0.0
    assert score["shift_score"] > 0.0
    assert score["critical_band_delta_p"] > 0.0
    assert score["cost_gate"] == pytest.approx(1.0)


def test_tps_caps_bad_defense_at_zero_but_raw_net_can_be_negative():
    rows_no = [_row(0.0, 0.0, 0.01), _row(0.01, 0.0, 0.01), _row(0.02, 1.0, 0.10)]
    rows_def = [
        _row(0.0, 1.0, 0.20, utility=10.0, fp=1.0, cost=10.0),
        _row(0.01, 1.0, 0.20, utility=10.0, fp=1.0, cost=10.0),
        _row(0.02, 1.0, 0.20, utility=10.0, fp=1.0, cost=10.0),
    ]

    score = threshold_protection_score(rows_no, rows_def, alphas=[0.0, 0.01, 0.02])

    assert score["tps"] == 0.0
    assert score["raw_net"] < 0.0


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


def test_exp8_sensitivity_reports_alpha_c_delta():
    rows = [
        {"scenario": "s1", "family": "feedback_strength", "value": "0.4", "alpha": 0.01, "collapse_rate_mean": 0.0},
        {"scenario": "s1", "family": "feedback_strength", "value": "0.4", "alpha": 0.02, "collapse_rate_mean": 1.0},
        {"scenario": "s1", "family": "feedback_strength", "value": "1.2", "alpha": 0.01, "collapse_rate_mean": 0.0},
        {"scenario": "s1", "family": "feedback_strength", "value": "1.2", "alpha": 0.03, "collapse_rate_mean": 1.0},
    ]
    alpha_rows = _alpha_c_rows(rows)
    deltas = _family_delta_rows(alpha_rows, scenarios=["s1"], families=["feedback_strength"])

    assert len(alpha_rows) == 2
    assert deltas[0]["delta_alpha_c"] == pytest.approx(0.005)


def test_exp10_delta_rows_report_expected_sign_and_ci(monkeypatch):
    monkeypatch.setattr(
        "experiments.scaling_theory.exp10_comparative_statics_threshold.CI_BOOT",
        10,
    )
    raw_rows = []
    for variant, value, collapses in [
        ("base", "1.0", [(0.01, 0.0), (0.02, 1.0), (0.03, 1.0)]),
        ("changed", "1.5", [(0.01, 0.0), (0.02, 0.0), (0.03, 1.0)]),
    ]:
        for alpha, collapse in collapses:
            for seed in [1, 2, 3]:
                raw_rows.append({
                    "scenario": "s1",
                    "lever": "asset_liquidity_scale",
                    "variant": variant,
                    "lever_value": value,
                    "alpha": alpha,
                    "seed": seed,
                    "collapse_rate": collapse,
                })
    alpha_rows = [
        {
            "scenario": "s1",
            "n_society": 1000,
            "lever": "asset_liquidity_scale",
            "variant": "base",
            "lever_value": "1.0",
            "alpha_c": 0.015,
        },
        {
            "scenario": "s1",
            "n_society": 1000,
            "lever": "asset_liquidity_scale",
            "variant": "changed",
            "lever_value": "1.5",
            "alpha_c": 0.025,
        },
    ]

    rows = _delta_rows(alpha_rows, raw_rows, {"s1": [0.01, 0.02, 0.03]})

    assert rows[0]["delta_alpha_c"] == pytest.approx(0.01)
    assert rows[0]["expected_sign"] == "positive"
    assert rows[0]["observed_sign"] == "positive"
    assert rows[0]["sign_pass"] is True
    assert rows[0]["delta_bootstrap_successes"] > 0


def test_exp7_main_table_includes_clean_cost_and_worst_score(monkeypatch):
    monkeypatch.setattr(
        "experiments.defense_benchmark.exp7_threshold_shift_defense.DEFENSES",
        ["topology_aware"],
    )
    summary_rows = [
        {
            "scenario": "s1",
            "n_society": 100,
            "defense": "topology_aware",
            "alpha_c_no_def": 0.01,
            "alpha_c_def": 0.02,
            "threshold_shift": 0.01,
            "threshold_shift_raw_or_bound": 0.01,
            "defense_score": 5.0,
            "utility_loss": 0.2,
            "false_positive_rate": 0.0,
            "intervention_cost": 0.2,
        },
        {
            "scenario": "s2",
            "n_society": 100,
            "defense": "topology_aware",
            "alpha_c_no_def": 0.001,
            "alpha_c_def": 0.0015,
            "threshold_shift": 0.0005,
            "threshold_shift_raw_or_bound": 0.0005,
            "defense_score": -1.0,
            "utility_loss": 0.1,
            "false_positive_rate": 0.0,
            "intervention_cost": 0.1,
        },
    ]
    raw_rows = [
        {
            "scenario_id": "s1",
            "n_society": 100,
            "defense": "topology_aware",
            "alpha": 0.0,
            "utility_loss": 0.03,
            "false_positive_rate": 0.02,
        }
    ]

    table = _main_table(summary_rows, raw_rows)

    assert table[0]["clean_utility_cost"] == pytest.approx(0.03)
    assert table[0]["clean_false_positive_rate"] == pytest.approx(0.02)
    assert table[0]["worst_score"] == pytest.approx(-1.0)
