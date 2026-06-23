# ICLR Evidence Package

This checklist tracks the non-baseline work needed to make WolfBench credible
for an ICLR submission.

## Scope

In scope:

- Theory reframing and testable scaling predictions.
- Higher-confidence scaling and leaderboard statistics.
- External calibration notes and sensitivity audits.
- Cross-mechanism critical-regime experiments.
- Paper wording changes that define the law as a protocol-specific empirical
  finite-size scaling ansatz and avoid overclaiming strict phase transitions.

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
WOLFBENCH_EXP2_N_GRID=100,150,200,300,500,750,1000,1500,2000,3000,5000 \
python -m experiments.scaling_theory.exp2_society_size_scaling
```

Scaling-law post-processing:

```bash
python -m experiments.scaling_theory.analyze_scaling_law
python -m experiments.paper_figures
```

Cross-mechanism audit:

```bash
WOLFBENCH_EXP7_SEEDS=$(seq -s, 1 50) \
python -m experiments.scaling_theory.exp7_cross_mechanism_threshold
```

Canonical S1-S4 scaling evidence:

```bash
WOLFBENCH_EXP12_SEEDS=$(seq -s, 1 30) \
WOLFBENCH_EXP12_N_GRID=500,1000,2000 \
python -m experiments.scaling_theory.exp12_canonical_scaling
```

Use Exp12 for paper-facing four-scenario claims. It reports one
scenario-aligned `primary_failure` curve per scenario/N: generic collapse for
S1/S2, spoofing/liquidity failure for S3, and fake-liquidity failure for S4.
Treat S2 as a low-count threshold case at N=`500,1000,2000`: the visible jump is
the first-finfluencer boundary, while S3/S4 require locally dense alpha grids
around their mechanism thresholds.

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

- Use Exp12 `alpha_c_by_scenario_n.csv`, `failure_curves.csv`, and
  `scenario_law_summary.csv` for paper-facing S1-S4 mechanism-aligned scaling
  claims. Use Exp2 `alpha_critical_summary.csv` for the dense S1 finite-size law.
- Use `paperoutputs/scaling/scaling_law_audit/exp2_dense_law_summary.csv` for
  the law claim. Report all-N and `N >= 500` exponents, bootstrap exponent CIs,
  leave-one-N-out ranges, and the evidence grade.
- Use Wilson intervals for binary `P(collapse)` plots.
- Use bootstrap CIs for logistic `alpha_c` and leaderboard means.
- Report seed-level rank stability from `exp6` summary JSON.
- Report sensitivity results as robust regions, not as proof of one exact
  calibrated parameter point.

## Claim Boundary

- Allowed: "empirical finite-size scaling law under the S1 WolfBench protocol"
  when the dense Exp2 run has stable exponent diagnostics.
- Allowed fallback: "finite-size scaling trend" when the exponent is noisy or
  leave-one-N-out diagnostics are unstable.
- Not allowed: universal financial-market law, thermodynamic phase transition,
  universal exponent across S1-S4, or asymptotic theorem.