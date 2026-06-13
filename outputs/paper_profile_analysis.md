# Paper Profile Analysis

Generated: 2026-06-09
Repo commit: `cf4d06c`

## Exp2: S1 Society-Size Scaling

Source: `outputs/scaling_theory/exp2_society_size_scaling/`

| N | alpha_c logistic | 95% CI | transition width | slope |
|---:|---:|---:|---:|---:|
| 100 | 0.01439 | [0.01278, 0.01610] | 0.03662 | 119.99 |
| 200 | 0.01516 | [0.01336, 0.01694] | 0.04448 | 98.80 |
| 500 | 0.01377 | [0.01232, 0.01533] | 0.03613 | 121.62 |
| 1000 | 0.01236 | [0.01115, 0.01355] | 0.02348 | 187.16 |
| 2000 | 0.01126 | [0.01008, 0.01240] | 0.02081 | 211.13 |
| 5000 | 0.00937 | [0.00817, 0.01049] | 0.01826 | 240.62 |

Key readout: alpha_c declines from 0.01439 at N=100 to 0.00937 at N=5000; transition width also narrows from 0.03662 to 0.01826.

## Exp7: Cross-Mechanism Critical-Regime Audit

Source: `outputs/scaling_theory/exp7_cross_mechanism_threshold/`

| Scenario | N | alpha_c logistic | 95% CI | method | transition width |
|---|---:|---:|---:|---|---:|
| S1 | 500 | 0.01346 | [0.01169, 0.01508] | logistic_fit | 0.03392 |
| S1 | 1000 | 0.01283 | [0.01145, 0.01404] | logistic_fit | 0.02254 |
| S1 | 2000 | 0.01176 | [0.01035, 0.01291] | logistic_fit | 0.01913 |
| S2 | 500 | 0.00113 | [0.00103, 0.00118] | logistic_fit | 0.00083 |
| S2 | 1000 | 0.00057 | [0.00044, 0.00059] | logistic_fit | 0.00028 |
| S2 | 2000 | 0.00028 | [0.00018, 0.00033] | logistic_fit | 0.00057 |
| S3 | 500 |  |  | linear_fallback_constant_curve |  |
| S3 | 1000 | 0.54999 | [0.54999, 0.54999] | logistic_fit | 0.01591 |
| S3 | 2000 | 0.37499 | [0.37499, 0.37499] | logistic_fit | 0.00801 |
| S4 | 500 | 0.05842 | [0.03090, 0.10579] | logistic_fit | 0.66357 |
| S4 | 1000 | 0.07602 | [0.03897, 0.15000] | logistic_fit | 0.92655 |
| S4 | 2000 | 0.11224 | [0.05921, 0.15000] | logistic_fit | 1.22547 |

Grid note: S3/N=500 did not yield a finite logistic alpha_c on the current alpha grid; report this as a grid-coverage limitation rather than a failed run.

## Exp8: Parameter Sensitivity Audit

Source: `outputs/scaling_theory/exp8_sensitivity_audit/`

| Scenario | Family | min P(collapse) | max P(collapse) | delta | value at min | value at max |
|---|---|---:|---:|---:|---|---|
| S1 | asset_liquidity_scale | 0.500 | 0.600 | 0.100 | 2.0 | 0.5 |
| S1 | feedback_strength | 0.540 | 0.540 | 0.000 | 0.0 | 0.0 |
| S1 | placement | 0.540 | 1.000 | 0.460 | random | high_degree |
| S1 | retail_risk_appetite | 0.540 | 0.540 | 0.000 | 0.01 | 0.01 |
| S1 | retail_wealth_scale | 0.500 | 0.600 | 0.100 | 0.5 | 2.0 |
| S1 | social_mean_degree | 0.400 | 1.000 | 0.600 | 4 | 12 |
| S2 | asset_liquidity_scale | 0.760 | 1.000 | 0.240 | 2.0 | 0.5 |
| S2 | feedback_strength | 0.980 | 0.980 | 0.000 | 0.0 | 0.0 |
| S2 | placement | 0.200 | 0.980 | 0.780 | random | high_degree |
| S2 | retail_risk_appetite | 0.700 | 1.000 | 0.300 | 0.01 | 0.04 |
| S2 | retail_wealth_scale | 0.760 | 1.000 | 0.240 | 0.5 | 2.0 |
| S2 | social_mean_degree | 0.800 | 1.000 | 0.200 | 4 | 16 |
| S3 | asset_liquidity_scale | 0.000 | 1.000 | 1.000 | 0.75 | 0.5 |
| S3 | feedback_strength | 0.000 | 0.000 | 0.000 | 0.0 | 0.0 |
| S3 | placement | 0.000 | 0.000 | 0.000 | random | random |
| S3 | retail_risk_appetite | 0.000 | 0.000 | 0.000 | 0.01 | 0.01 |
| S3 | retail_wealth_scale | 0.000 | 0.000 | 0.000 | 0.5 | 0.5 |
| S3 | social_mean_degree | 0.000 | 0.000 | 0.000 | 4 | 4 |
| S4 | asset_liquidity_scale | 0.500 | 0.540 | 0.040 | 0.5 | 0.75 |
| S4 | feedback_strength | 0.520 | 0.520 | 0.000 | 0.0 | 0.0 |
| S4 | placement | 0.520 | 0.520 | 0.000 | random | random |
| S4 | retail_risk_appetite | 0.500 | 0.540 | 0.040 | 0.04 | 0.01 |
| S4 | retail_wealth_scale | 0.500 | 0.540 | 0.040 | 2.0 | 0.5 |
| S4 | social_mean_degree | 0.520 | 0.520 | 0.000 | 4 | 4 |

Strongest sensitivity deltas:
- S3 / asset_liquidity_scale: delta P(collapse) = 1.000
- S2 / placement: delta P(collapse) = 0.780
- S1 / social_mean_degree: delta P(collapse) = 0.600
- S1 / placement: delta P(collapse) = 0.460
- S2 / retail_risk_appetite: delta P(collapse) = 0.300
- S2 / retail_wealth_scale: delta P(collapse) = 0.240
- S2 / asset_liquidity_scale: delta P(collapse) = 0.240
- S2 / social_mean_degree: delta P(collapse) = 0.200

## Exp6: Defense Leaderboard Paper Profile

Source: `outputs/defense_benchmark/exp6_paper50/`

Completed: 2026-06-09T19:54:54Z. The run used 50 seeds, N={500, 1000, 2000}, and the built-in CPU-only defenses `noguard`, `random`, `rule`, and `oracle`. `oracle` is reported as an upper-bound track, not an eligible defense.

| Defense model | S1 | S2 | S3 | S4 | Avg DefenseScore | Avg ThresholdShift | Worst Score |
|---|---:|---:|---:|---:|---:|---:|---:|
| random | -6.72 | 14.53 | -0.82 | -2.30 | 1.17 | -0.0024 | -6.72 |
| noguard | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.0000 | 0.00 |
| oracle | -2.11 | 0.04 | -0.78 | 1.78 | -0.27 | -0.0021 | -2.11 |
| rule | -13.57 | -0.01 | -1.69 | -17.44 | -8.18 | -0.0007 | -17.44 |

Eligible-defense readout: `random` is the only eligible defense above `noguard` on average, with Avg DefenseScore 1.17, but this is driven almost entirely by S2. It is negative on S1, S3, and S4, and has a negative average threshold shift. `rule` reduces harm in some cells but pays very high utility/intervention cost, giving the worst overall score.

Upper-bound readout: `oracle` is not eligible and still averages slightly below `noguard` under the current score because benefits are scenario-dependent and intervention cost remains nontrivial. It is strongest on S4 and poor on S1/S3.

Rank stability: seed-bootstrap Kendall tau is 0.976 with 95% CI [0.667, 1.000]; top-1 overlap is 1.000 with 95% CI [1.000, 1.000]. The reference ranking is `oracle > noguard > random > rule` at the seed-level stability calculation, while the aggregate eligible leaderboard ranks `random > noguard > rule`.

Interpretation caution: the current built-in defenses are weak paper baselines, not competitive mitigation methods. The leaderboard is useful as a no-strong-defense diagnostic table, but the paper still needs stronger defense baselines before claiming defense benchmark strength.

