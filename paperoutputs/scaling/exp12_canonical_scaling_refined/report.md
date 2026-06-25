# Exp12 Canonical Scaling Evidence

Primary-failure convention: S1/S2 use generic collapse, S3 uses spoofing/liquidity failure, and S4 uses fake-liquidity failure.
Generic collapse remains in data.csv and failure_curves.csv as a diagnostic field.

Scenarios: s1, s2, s3, s4
N grid: [500, 1000, 2000, 10000]
Seeds: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30]
CI bootstrap draws: 1000

## Scenario Summary

| scenario | primary metric | crossings | mean curve delta | width slope | grade | caveat |
|---|---|---:|---:|---:|---|---|
| S1 | generic_collapse | 4/4 | 0.7667 | -0.0734 | strong | All tested N values cross the primary-failure threshold and fitted width narrows with N. |
| S2 | generic_collapse | 3/4 | 0.6000 | -0.9414 | partial | Threshold evidence is present, but one N or width trend needs denser calibration. |
| S3 | spoof_liquidity_failure | 4/4 | 1.0000 | -0.0024 | strong | All tested N values cross the primary-failure threshold and fitted width narrows with N. |
| S4 | fake_liquidity_failure | 4/4 | 0.9500 | -0.3294 | mechanism-strong | S4 is evaluated with fake-liquidity primary failure; generic collapse width is diagnostic only. |

## Alpha-C By Scenario And N

| scenario | N | alpha_c | 95% CI | width 10-90 | coverage | fit |
|---|---:|---:|---|---:|---|---|
| S1 | 500 | 0.0127 | [0.0102, 0.0150] | 0.0345 | crosses_0.5 | logistic_fit |
| S1 | 1000 | 0.0126 | [0.0106, 0.0143] | 0.0232 | crosses_0.5 | logistic_fit |
| S1 | 2000 | 0.0115 | [0.0095, 0.0131] | 0.0204 | crosses_0.5 | logistic_fit |
| S1 | 10000 | 0.0057 | [0.0022, 0.0086] | 0.0254 | crosses_0.5 | logistic_fit |
| S2 | 500 | 0.0007 | [0.0007, 0.0008] | 0.0020 | crosses_0.5 | logistic_fit |
| S2 | 1000 | 0.0004 | [0.0003, 0.0004] | 0.0009 | crosses_0.5 | logistic_fit |
| S2 | 2000 | 0.0002 | [0.0002, 0.0002] | 0.0004 | crosses_0.5 | logistic_fit |
| S2 | 10000 | 0.0000 | [0.0000, 0.0000] | 0.0001 | left_censored_above_threshold | logistic_fit |
| S3 | 500 | 0.0887 | [0.0887, 0.0887] | 0.0004 | crosses_0.5 | logistic_fit |
| S3 | 1000 | 0.0638 | [0.0638, 0.0638] | 0.0004 | crosses_0.5 | logistic_fit |
| S3 | 2000 | 0.0438 | [0.0438, 0.0438] | 0.0004 | crosses_0.5 | logistic_fit |
| S3 | 10000 | 0.0188 | [0.0188, 0.0188] | 0.0004 | crosses_0.5 | logistic_fit |
| S4 | 500 | 0.0241 | [0.0232, 0.0253] | 0.0130 | crosses_0.5 | logistic_fit |
| S4 | 1000 | 0.0226 | [0.0216, 0.0235] | 0.0112 | crosses_0.5 | logistic_fit |
| S4 | 2000 | 0.0225 | [0.0217, 0.0235] | 0.0082 | crosses_0.5 | logistic_fit |
| S4 | 10000 | 0.0237 | [0.0230, 0.0244] | 0.0050 | crosses_0.5 | logistic_fit |
