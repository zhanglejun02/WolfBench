# Exp12 Canonical Scaling Evidence

Primary-failure convention: S1/S2 use generic collapse, S3 uses spoofing/liquidity failure, and S4 uses fake-liquidity failure.
Generic collapse remains in data.csv and failure_curves.csv as a diagnostic field.

Scenarios: s1, s2, s3, s4
N grid: [500]
Seeds: [1]
CI bootstrap draws: 20

## Scenario Summary

| scenario | primary metric | crossings | mean curve delta | width slope | grade | caveat |
|---|---|---:|---:|---:|---|---|
| S1 | generic_collapse | 0/1 | 0.0000 |  | inconclusive | Alpha grid or primary-failure threshold needs calibration before making a strong law claim. |
| S2 | generic_collapse | 0/1 | 0.0000 |  | inconclusive | Alpha grid or primary-failure threshold needs calibration before making a strong law claim. |
| S3 | spoof_liquidity_failure | 1/1 | 1.0000 |  | partial | Threshold evidence is present, but one N or width trend needs denser calibration. |
| S4 | fake_liquidity_failure | 1/1 | 1.0000 |  | mechanism-strong | S4 is evaluated with fake-liquidity primary failure; generic collapse width is diagnostic only. |

## Alpha-C By Scenario And N

| scenario | N | alpha_c | 95% CI | width 10-90 | coverage | fit |
|---|---:|---:|---|---:|---|---|
| S1 | 500 |  | [, ] |  | right_censored_below_threshold | linear_fallback_constant_curve |
| S2 | 500 |  | [, ] |  | right_censored_below_threshold | linear_fallback_constant_curve |
| S3 | 500 | 0.4500 | [0.4500, 0.4500] |  | crosses_0.5 | linear_fallback_constant_curve |
| S4 | 500 | 0.0750 | [0.0750, 0.0750] |  | crosses_0.5 | linear_fallback_constant_curve |
