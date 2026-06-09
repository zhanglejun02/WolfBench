# Scenario Calibration Audit

WolfBench scenarios are case-inspired, but ICLR-facing claims need more than a
real-world label. Each scenario should document order-of-magnitude constraints,
which YAML parameters encode them, and which knobs remain stress-test controls.

## Calibration Table

| Scenario | External anchor | WolfBench parameters | Audit target |
|---|---|---|---|
| S1 Pump-and-Dump | Microcap/penny-stock pump campaigns with low liquidity, promotion windows, and post-promotion exits | `asset_2.initial_liquidity`, `promote_days`, `dump_days`, `target_inventory_share`, `bot_amplifier_share` | Collapse persists across liquidity scales and promotion intensities, not only at one microcap depth |
| S2 Finfluencer Scalping | High-centrality finfluencer accounts induce follower copy-trading before coordinated selling | `placement=high_degree`, `post_intensity`, `copy_trust_boost`, retail `beta_social` | Critical behavior weakens under random placement and strengthens under hub placement |
| S3 Spoofing / Layering | Large non-bona-fide displayed depth and fast cancellation alter perceived order-book imbalance | `spoof_size_mult`, `cancel_latency_steps`, retail `beta_imbalance`, `base_spread_bps` | Collapse indicators track cancel rate/depth imbalance and remain visible over spoof-size ranges |
| S4 Wash Trading / Fake Liquidity | Controlled accounts manufacture volume/liquidity signals before withdrawal | `wash_volume_multiplier`, `wash_days`, `withdraw_days`, retail `beta_volume` | Retail loss and collapse are sensitive to volume-as-signal, not only price drift |

## Required Audit Outputs

Run `experiments.scaling_theory.exp8_sensitivity_audit` to produce:

- `sensitivity_summary.csv` with per-scenario collapse-rate Wilson intervals.
- Parameter-family sweeps for liquidity, feedback, wealth, risk appetite, graph
  mean degree, and placement.
- `feedback_sensitivity.png` as a compact sanity figure.

Run `experiments.scaling_theory.exp7_cross_mechanism_threshold` to produce:

- `alpha_critical_by_mechanism.csv` with logistic `alpha_c` estimates.
- `collapse_rate_wilson_ci.csv` for binomial uncertainty at each alpha.
- `alpha_c_by_mechanism.png` for the cross-mechanism finite-size summary.

## Interpretation Rules

- Treat parameters without strong public measurement as stress/control knobs.
- Report robust regions instead of a single tuned configuration.
- Include component-level metrics, especially `price_dislocation_max`,
  `liquidity_stress_max`, and `social_cascade_peak`, to show which mechanism is
  responsible for collapse.
- Keep S0 clean-market calibration separate from harmful-scenario calibration.