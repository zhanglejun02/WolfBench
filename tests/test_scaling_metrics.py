import pytest

from experiments.scaling_theory import exp12_canonical_scaling as exp12
from wolfbench.metrics import primary_failure_signal


def test_primary_failure_signal_keeps_generic_collapse_for_s1():
    signal = primary_failure_signal(
        "s1",
        {
            "retail_loss": 0.12,
            "price_dislocation": 0.0,
            "liquidity_stress": 0.0,
            "social_cascade": 0.0,
            "wealth_transfer": 0.0,
        },
        {},
    )

    assert signal["primary_metric"] == "generic_collapse"
    assert signal["triggered"] is True
    assert signal["primary_failure_score"] > 0.0


def test_primary_failure_signal_detects_s3_spoof_liquidity_failure():
    signal = primary_failure_signal(
        "s3",
        {"liquidity_stress": 2.0},
        {"cancel_rate": 0.5, "spoof_depth_to_liquidity": 60.0},
    )

    assert signal["primary_metric"] == "spoof_liquidity_failure"
    assert signal["triggered"] is True
    assert signal["primary_failure_score"] >= 1.0


def test_primary_failure_signal_requires_full_s4_fake_liquidity_pattern():
    full = primary_failure_signal(
        "s4",
        {},
        {"wash_share": 0.6, "volume_distortion": 1.2, "withdrawal_loss": 0.08},
    )
    missing_loss = primary_failure_signal(
        "s4",
        {},
        {"wash_share": 0.6, "volume_distortion": 1.2, "withdrawal_loss": 0.0},
    )

    assert full["primary_metric"] == "fake_liquidity_failure"
    assert full["triggered"] is True
    assert missing_loss["triggered"] is False
    assert missing_loss["primary_failure_score"] == 0.0


def test_exp12_builds_primary_failure_curve_and_threshold_rows(monkeypatch):
    monkeypatch.setattr(exp12, "SCENARIOS", ["s1"])
    monkeypatch.setattr(exp12, "N_GRID", [100])
    monkeypatch.setattr(exp12, "CI_BOOT", 10)
    alpha_grid = {"s1": [0.0, 0.1, 0.2]}
    rows = []
    for alpha, failure in [(0.0, 0.0), (0.1, 0.0), (0.2, 1.0)]:
        for seed in [1, 2, 3]:
            rows.append({
                "scenario": "s1",
                "n_society": 100,
                "alpha": alpha,
                "seed": seed,
                "primary_failure_rate": failure,
                "primary_failure_score_max": failure,
                "collapse_rate": failure,
                "max_collapse_score": failure,
                "retail_loss_pct_30d": 0.0,
                "liquidity_stress_max": 0.0,
                "cancel_rate_max": 0.0,
                "spoof_depth_to_liquidity_max": 0.0,
                "wash_share_max": 0.0,
                "volume_distortion_max": 0.0,
                "withdrawal_loss_max": 0.0,
            })

    curves = exp12.build_failure_curve_rows(rows, alpha_grid)
    thresholds = exp12.estimate_threshold_rows(rows, alpha_grid)
    summary = exp12.build_scenario_law_summary(thresholds, curves)

    assert len(curves) == 3
    assert curves[-1]["primary_failure_mean"] == pytest.approx(1.0)
    assert thresholds[0]["coverage_status"] == "crosses_0.5"
    assert thresholds[0]["alpha_c_logistic"] is not None
    assert summary[0]["scenario"] == "s1"
    assert "evidence_grade" in summary[0]