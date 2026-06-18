# Harmful-Agent Finite-Size Scaling Model

This note frames WolfBench as a finite-size critical-regime benchmark. The goal
is not to claim a thermodynamic phase transition. The goal is to define
estimands that can be fitted, shifted by interventions, and checked across
mechanisms. The word "law" should be read as a protocol-specific empirical
scaling relation, not as a universal physical law.

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

## Proposition 1: Estimated Critical Harmful Ratio

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

This is a statistical critical-regime definition, not an asymptotic theorem. The
evidence target is a reproducible midpoint `alpha_c`, transition sharpening as
`N` grows, and exponent stability under bootstrap and leave-one-`N`-out checks.

## Finite-Size Scaling Ansatz

The primary scaling ansatz for the fixed S1 protocol is

```text
alpha_c(N) = alpha_inf + a N^{-nu}
w_N = b N^{-gamma}
```

The conservative main-text form is the pure power relation

```text
alpha_c(N) ~= A N^{-nu}
```

because a finite asymptote `alpha_inf` is harder to identify from a moderate
number of finite `N` values. The finite-asymptote model should be reported as a
diagnostic unless the dense Exp2 run identifies a positive `alpha_inf` with a
stable confidence interval.

This gives a three-level evidence ladder:

| Evidence level | Required support | Paper wording |
| --- | --- | --- |
| Diagnostic trend | Few `N` points or unstable leave-one-out exponents | "finite-size scaling trend" |
| Law candidate | Dense `N` grid, bootstrap exponent CI, stable leave-one-out range | "empirical finite-size scaling law under the S1 protocol" |
| Universal law | Same exponent across mechanisms and protocol variants | Not claimed |

The canonical run for the law candidate is dense Exp2 with
`N = 100,150,200,300,500,750,1000,1500,2000,3000,5000`, the near-threshold alpha
grid, and 50 seeds. Report both all-`N` and `N >= 500` fits. The latter is a
stable-regime robustness row that reduces sensitivity to small-`N` finite-size
noise.

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

The same estimator applies across mechanisms, but the exponent is not assumed to
be universal. Each scenario has a mechanism-specific `alpha_c^m(N)`, transition
width, and dominant amplification channel. S1 is the canonical law experiment;
S2-S4 test whether the estimator transfers to other mechanisms.

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

- Exp2 is the canonical finite-size scaling experiment for Proposition 1. Dense
   Exp2 is the only experiment that should carry the main law claim.
- Exp5 is a capacity-confound robustness check, not the main theory test.
- Exp7 establishes that mechanisms have different `alpha_c^m(N)` scales and
   should not be used to claim a universal exponent.
- Exp8 should be upgraded from probability sensitivity to threshold-shift
  comparative statics for Proposition 2.
- Defense benchmark experiments should add alpha sweeps and report
  `ThresholdShift` for Proposition 3.

Use phrases such as "finite-size scaling ansatz", "finite-size threshold
behavior", "critical harmful-agent regime", "estimated critical ratio", and
"protocol-specific empirical law". Avoid claiming a strict phase transition,
thermodynamic limit, universal exponent, or asymptotic theorem.