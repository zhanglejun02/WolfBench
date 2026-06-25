# Exp12 Canonical Scaling Evidence

Primary-failure convention: S1/S2 use generic collapse, S3 uses spoofing/liquidity failure, and S4 uses fake-liquidity failure.
Generic collapse remains in data.csv and failure_curves.csv as a diagnostic field.

Scenarios: s1, s2, s3, s4
N grid: [500, 1000, 2000]
Seeds: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30]
CI bootstrap draws: 1000

## Scenario Summary

| scenario | primary metric | crossings | mean curve delta | width slope | grade | caveat |
|---|---|---:|---:|---:|---|---|
| S1 | generic_collapse | 3/3 | 0.8111 | -0.3796 | strong | All tested N values cross the primary-failure threshold and fitted width narrows with N. |
| S2 | generic_collapse | 3/3 | 0.7111 | -1.2593 | strong | All tested N values cross the primary-failure threshold and fitted width narrows with N. |
| S3 | spoof_liquidity_failure | 3/3 | 1.0000 | 0.0000 | partial | Threshold evidence is present, but one N or width trend needs denser calibration. |
| S4 | fake_liquidity_failure | 3/3 | 0.9556 | -0.6543 | mechanism-strong | S4 is evaluated with fake-liquidity primary failure; generic collapse width is diagnostic only. |

## Alpha-C By Scenario And N

| scenario | N | alpha_c | 95% CI | width 10-90 | coverage | fit |
|---|---:|---:|---|---:|---|---|
| S1 | 500 | 0.0127 | [0.0102, 0.0150] | 0.0345 | crosses_0.5 | logistic_fit |
| S1 | 1000 | 0.0126 | [0.0106, 0.0143] | 0.0232 | crosses_0.5 | logistic_fit |
| S1 | 2000 | 0.0115 | [0.0095, 0.0131] | 0.0204 | crosses_0.5 | logistic_fit |
| S2 | 500 | 0.0008 | [0.0007, 0.0011] | 0.0016 | crosses_0.5 | logistic_fit |
| S2 | 1000 | 0.0005 | [0.0003, 0.0006] | 0.0009 | crosses_0.5 | logistic_fit |
| S2 | 2000 | 0.0003 | [0.0002, 0.0003] | 0.0003 | crosses_0.5 | logistic_fit |
| S3 | 500 | 0.0750 | [0.0750, 0.0750] | 0.0239 | crosses_0.5 | logistic_fit |
| S3 | 1000 | 0.0750 | [0.0750, 0.0750] | 0.0239 | crosses_0.5 | logistic_fit |
| S3 | 2000 | 0.0750 | [0.0750, 0.0750] | 0.0239 | crosses_0.5 | logistic_fit |
| S4 | 500 | 0.0254 | [0.0227, 0.0306] | 0.0212 | crosses_0.5 | logistic_fit |
| S4 | 1000 | 0.0201 | [0.0198, 0.0238] | 0.0020 | crosses_0.5 | logistic_fit |
| S4 | 2000 | 0.0232 | [0.0205, 0.0250] | 0.0086 | crosses_0.5 | logistic_fit |
