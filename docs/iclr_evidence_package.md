# ICLR Evidence Package

This checklist tracks the non-baseline work needed to make WolfBench credible
for an ICLR submission.

## Scope

In scope:

- Theory reframing and testable scaling predictions.
- Higher-confidence scaling and leaderboard statistics.
- External calibration notes and sensitivity audits.
- Cross-mechanism critical-regime experiments.
- Paper wording changes that avoid overclaiming strict phase transitions.

Out of scope for this pass:

- New market/social/hybrid defense baselines.

## Recommended Runs

Quick smoke run:

```bash
WOLFBENCH_EXP2_SEEDS=1,2 \
WOLFBENCH_EXP2_N_GRID=200 \
WOLFBENCH_EXP2_ALPHAS=0.0,0.01,0.02 \
python -m experiments.scaling_theory.exp2_society_size_scaling
```

Paper scaling run:

```bash
WOLFBENCH_EXP2_SEEDS=$(seq -s, 1 50) \
python -m experiments.scaling_theory.exp2_society_size_scaling
```

Cross-mechanism audit:

```bash
WOLFBENCH_EXP7_SEEDS=$(seq -s, 1 50) \
python -m experiments.scaling_theory.exp7_cross_mechanism_threshold
```

Sensitivity audit:

```bash
WOLFBENCH_EXP8_SEEDS=$(seq -s, 1 50) \
python -m experiments.scaling_theory.exp8_sensitivity_audit
```

Paper leaderboard profile:

```bash
WOLFBENCH_EXP6_SEEDS=$(seq -s, 1 50) \
WOLFBENCH_EXP6_OUT=exp6_paper50 \
python -m experiments.defense_benchmark.exp6_defense_leaderboard
```

## Reporting Requirements

- Use `alpha_critical_summary.csv` and `alpha_critical_by_mechanism.csv` for the
  main `alpha_c` claims.
- Use Wilson intervals for binary `P(collapse)` plots.
- Use bootstrap CIs for logistic `alpha_c` and leaderboard means.
- Report seed-level rank stability from `exp6` summary JSON.
- Report sensitivity results as robust regions, not as proof of one exact
  calibrated parameter point.