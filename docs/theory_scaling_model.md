# Harmful-Agent Scaling Model

This note reframes the WolfBench theory claim as a finite-size critical-regime
prediction rather than a standalone strict phase-transition theorem.

## Mechanism Sketch

WolfBench episodes couple three amplifying channels:

1. Harmful agents generate market pressure, social exposure, or microstructure
   artifacts against a target asset.
2. Retail agents convert exposure into buy/sell probability through role-specific
   susceptibility weights.
3. Market impact converts net retail flow into price dislocation, which can feed
   back into social exposure and momentum demand.

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

## Testable Predictions

The model is useful only if it yields predictions that the experiments can
falsify. The paper evidence package should test:

- Higher liquidity increases `alpha_c` and lowers price-dislocation components.
- Higher graph centrality or mean degree lowers `alpha_c` for social mechanisms.
- Higher `feedback_strength` increases collapse probability near threshold.
- Higher retail risk appetite lowers `alpha_c` by increasing impact per exposed
  retail account.
- Cross-mechanism scenarios should show different critical ratios, but the same
  finite-size critical-regime estimators should apply.

## Paper Positioning

The theorem should be described as an explanatory lemma: it shows that threshold
behavior is possible under coupled exposure and market-impact feedback. The main
contribution is the measurable protocol: estimate `P(collapse | N, alpha)`, fit
`alpha_c(N)`, and score defenses by whether they shift that critical regime.

Avoid claiming a thermodynamic phase transition. Use phrases such as
"finite-size threshold behavior", "critical harmful-agent regime", and
"estimated critical ratio".