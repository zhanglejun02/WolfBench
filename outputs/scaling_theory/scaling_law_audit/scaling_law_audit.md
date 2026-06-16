# Scaling-law audit

## Verdict

The current scaling package is enough for a predictive empirical-theory claim, but the evidence should be reorganized around three estimands: alpha_c(N), transition width, and threshold shift under interventions. Exp2 is already the main scaling-law experiment. Exp7 supports mechanism heterogeneity. Exp8 supports comparative statics at the probability level, but should be upgraded to alpha_c shifts for the paper's strongest causal-looking claims.

## Current fitted laws

- Exp2 S1 alpha_c power law: alpha_c ~= A * N^beta, with beta=-0.1163 and nu=0.1163. Log-space R2=0.8908.
- Exp2 S1 finite-asymptote fit: alpha_inf=3.323e-11, nu=0.1069. The fit collapses toward a near-zero alpha_inf, so current data do not identify a positive asymptotic threshold; use the pure power law in the main text.
- Exp2 S1 transition-width scaling: width ~= B * N^(-gamma), with gamma=0.2273. Log-space R2=0.8371.
- Stable-regime S1 alpha_c fit using N>=500: nu=0.1651. This is cleaner because N=100/200 have visible finite-size noise.
- Stable-regime S1 width fit using N>=500: gamma=0.2791.
- Exp7 S2 alpha_c fit: nu=1.011. This is the strongest cross-mechanism scaling signal.
- Exp7 S4 alpha_c fit: nu=-0.471. The sign is not expected to match S1 because S4's dominant channel is diffuse under the current collapse metric.

## Proposition alignment

| Theory claim | Current support | Weak point | Best experiment fix |
| --- | --- | --- | --- |
| Proposition 1: finite-size critical harmful ratio exists | Exp2 logistic alpha_c and width estimates; Exp7 S1/S2 thresholds | Exp2 summary has the power fit but not a dedicated scaling-law table; S3/S4 are not yet clean threshold examples | Keep Exp2 as main evidence; report both alpha_c and width exponents; make Exp7 explicitly mechanism-specific rather than universal |
| Proposition 2: comparative statics | Exp8 shows sensitivity ranges; Exp5 checks capacity confounding | Exp8 currently measures delta P(collapse), not delta alpha_c; derivative signs are therefore indirect | Add targeted threshold sweeps varying L, G, beta_social/risk, and placement, then report delta alpha_c and sign tests |
| Proposition 3: defense objective | Existing defense results can show loss reduction | There is no alpha_c(defense)-alpha_c(NoGuard) table yet | Add a defense threshold-shift experiment around S1/S2 critical grids and report ThresholdShift plus utility cost |
| Mechanism heterogeneity | Exp7 shows S1/S2/S3/S4 have different alpha_c scales; Exp8 shows different dominant sensitivities | S3 N=500 has no threshold in the current grid; S4 has a broad/flat transition | Give each mechanism its own dominant-channel prediction and alpha grid; do not force one universal exponent |

## Strongest Exp8 sensitivity evidence

- S3 / asset_liquidity_scale: delta=1 (0.75 -> 0.5)
- S2 / placement: delta=0.78 (random -> high_degree)
- S1 / social_mean_degree: delta=0.6 (4 -> 12)
- S1 / placement: delta=0.46 (random -> high_degree)
- S2 / retail_risk_appetite: delta=0.3 (0.01 -> 0.04)
- S2 / asset_liquidity_scale: delta=0.24 (2.0 -> 0.5)
- S2 / retail_wealth_scale: delta=0.24 (0.5 -> 2.0)
- S2 / social_mean_degree: delta=0.2 (4 -> 16)

## Recommended experiment optimization

1. Make Exp2 the canonical scaling law. Report alpha_c(N)=A*N^(-nu) as the conservative main fit. Mention alpha_c(N)=alpha_inf+a*N^(-nu) only as a robustness diagnostic because current data do not identify a positive alpha_inf. Use N>=500 as a robustness row because N=100/200 are noisy.
2. Add one plot and one CSV for transition width scaling. The width exponent is as important as alpha_c: it directly supports the finite-size critical-regime claim.
3. Reframe Exp5 as a confound check, not a main theorem test. It asks whether the S1 scaling survives capacity normalization. To make it cleaner, add N=500 and N=2000 or increase seeds at N=200 where the CI is very wide.
4. Upgrade Exp8 into a threshold-shift comparative-statics experiment. For each lever, run alpha grids around S1/S2 critical values and report delta alpha_c instead of only delta P(collapse). Minimal levers: asset_liquidity_scale, social_mean_degree, retail_risk_appetite, and placement.
5. Keep mechanism heterogeneity explicit. S1 should be social exposure plus price momentum; S2 high-centrality reach; S3 microstructure/liquidity stress; S4 volume-signal or wash-liquidity illusion. Each mechanism should get its own alpha grid and its own dominant-channel paragraph.
6. For S3, expand the N=500 alpha grid above 0.6 and use tighter grids around the observed N=1000 and N=2000 thresholds. The current N=500 constant/fallback row is a grid-coverage problem, not a theory result.
7. For S4, do not sell the current alpha_c slope as a failure or success. Treat it as a broad transition. Add component-level threshold metrics or a wider alpha grid up to roughly 0.25-0.30 to see whether the composite collapse metric saturates late.
8. Add a defense threshold-shift experiment: NoGuard, WolfGuard, and one simple baseline across alpha near the NoGuard alpha_c. The table should be alpha_c(defense), alpha_c(NoGuard), ThresholdShift, utility cost, and false-positive cost.

## Paper-facing interpretation

The strongest theory story is not a universal phase transition. It is a predictive finite-size framework: estimate P(collapse | N, alpha), summarize its midpoint alpha_c and width, then show how mechanism and controls shift those estimands. This turns the experiments into tests of the theory rather than illustrations after the fact.
