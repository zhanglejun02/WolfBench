# Harmful-Agent Scaling Model

This note frames WolfBench as a finite-size critical-regime benchmark. The goal
is not to claim a thermodynamic phase transition. The goal is to define
estimands that can be fitted, shifted by interventions, and checked across
mechanisms.

## Mechanism Sketch

WolfBench episodes couple three amplification channels:

1. Harmful agents generate market pressure, social exposure, or microstructure
   artifacts against a target asset.
2. Retail agents convert exposure into buy/sell probability through role-specific
   susceptibility weights.
3. Market impact converts net retail flow into price dislocation, which can feed
   back into social exposure, momentum demand, or perceived volume.

Let `alpha` be the harmful-agent ratio and approximate harmful exposure per day
as

```text
E_{t+1} = R_h(alpha, G, beta_s, phi) * E_t + eta_t
```

where `G` is graph reach/centrality, `beta_s` is retail social susceptibility,
and `phi` is social-market feedback. Market dislocation is approximated by

```text
D_t ~= kappa * Q_t / L
Q_t ~= beta_m * momentum_t + beta_s * E_t + beta_v * volume_signal_t
```

where `L` is effective liquidity and `kappa` is market-impact strength. A
finite-size critical regime appears when exposure reproduction and market-impact
feedback are large enough that retail flow pushes at least one CollapseScore
component over its threshold within the episode horizon.

## Proposition 1: Critical Harmful Ratio Exists

For a fixed mechanism `m`, society size `N`, liquidity `L`, graph exposure `G`,
and retail susceptibility vector `beta`, collapse probability is modeled by the
finite-size logistic estimator

```text
P(C = 1 | N, alpha, m) = sigmoid(s_N^m * (alpha - alpha_c^m(N)))
```

where `alpha_c^m(N)` is the estimated critical harmful ratio and `s_N^m` is the
local transition steepness. The corresponding transition width is

```text
w_N^m = alpha(P=0.9) - alpha(P=0.1) = 2 log(9) / s_N^m
```

This is a statistical critical-regime definition, not an asymptotic theorem.
The evidence target is a stable midpoint `alpha_c` plus transition sharpening as
`N` grows.

## Finite-Size Scaling Law

The primary scaling hypothesis is

```text
alpha_c^m(N) = alpha_inf^m + a_m N^{-nu_m}
w_N^m = b_m N^{-gamma_m}
```

The conservative reporting form is

```text
alpha_c^m(N) ~= A_m N^{-nu_m}
```

because the current number of `N` values is too small to identify a positive
`alpha_inf` strongly. In the current Exp2 S1 audit, the all-`N` power fit gives
`nu ~= 0.116`, while the cleaner `N >= 500` fit gives `nu ~= 0.165`. The
finite-asymptote fit collapses toward a near-zero `alpha_inf`, so it should be
reported only as a diagnostic. The transition width scales with `gamma ~= 0.227`
on all `N`, and `gamma ~= 0.279` on `N >= 500`.

## Proposition 2: Comparative Statics

The theory predicts that the critical harmful ratio shifts with dominant
amplification channels:

```text
partial alpha_c / partial L > 0
partial alpha_c / partial G < 0
partial alpha_c / partial beta_social < 0
partial alpha_c / partial placement_gain < 0
```

Probability-level sensitivity is useful diagnostics, but the paper-facing
estimand should be a threshold shift:

```text
Delta alpha_c(x) = alpha_c(x_high) - alpha_c(x_low)
```

Exp8 currently supports this proposition at the `Delta P(collapse)` level. A
stronger version should rerun targeted alpha grids for liquidity, graph degree,
retail susceptibility, and placement, then report `Delta alpha_c` with bootstrap
confidence intervals.

## Proposition 3: Defense Objective

A defense is effective when it moves the system away from the near-critical
region, not merely when it reduces average loss:

```text
ThresholdShift = alpha_c(defense) - alpha_c(NoGuard)
```

The desired regime is

```text
ThresholdShift > 0
UtilityCost is small
FalsePositiveCost is small
```

This turns defense evaluation into a critical-regime intervention test.

## Mechanism Heterogeneity

The same estimator applies across mechanisms, but `alpha_c^m(N)` is
mechanism-specific because each scenario has a different dominant amplification
channel.

| Scenario | Dominant channel | Theory interpretation |
| --- | --- | --- |
| S1 | Social exposure plus price momentum | Larger `G`, higher social susceptibility, and stronger feedback lower `alpha_c`. |
| S2 | High-centrality influencer reach | Placement and centrality dominate; very small `alpha` can be critical. |
| S3 | Microstructure and liquidity stress | Liquidity controls dominate; alpha grids must cover higher threshold values. |
| S4 | Volume-signal or wash-liquidity illusion | Collapse may be diffuse under the composite metric; use component-level checks and wider alpha grids. |

S4's broad or weak curve is therefore not automatically a theory failure. It is
evidence that the dominant channel is not captured as sharply by the current
collapse estimator.

## Experiment Alignment

- Exp2 is the canonical finite-size scaling experiment for Proposition 1.
- Exp5 is a capacity-confound robustness check, not the main theory test.
- Exp7 establishes that mechanisms have different `alpha_c^m(N)` scales.
- Exp8 should be upgraded from probability sensitivity to threshold-shift
  comparative statics for Proposition 2.
- Defense benchmark experiments should add alpha sweeps and report
  `ThresholdShift` for Proposition 3.

Use phrases such as "finite-size threshold behavior", "critical harmful-agent
regime", and "estimated critical ratio". Avoid claiming a strict phase
transition.