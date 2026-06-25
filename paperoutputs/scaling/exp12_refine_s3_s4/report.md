# Exp12 Canonical Scaling Evidence

Primary-failure convention: S1/S2 use generic collapse, S3 uses spoofing/liquidity failure, and S4 uses fake-liquidity failure.
Generic collapse remains in data.csv and failure_curves.csv as a diagnostic field.

Scenarios: s3, s4
N grid: [500, 1000, 2000]
Seeds: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30]
CI bootstrap draws: 1000

## Scenario Summary

| scenario | primary metric | crossings | mean curve delta | width slope | grade | caveat |
|---|---|---:|---:|---:|---|---|
| S3 | spoof_liquidity_failure | 3/3 | 1.0000 | -0.1657 | strong | All tested N values cross the primary-failure threshold and fitted width narrows with N. |
| S4 | fake_liquidity_failure | 3/3 | 0.9444 | -0.3353 | mechanism-strong | S4 is evaluated with fake-liquidity primary failure; generic collapse width is diagnostic only. |

## Alpha-C By Scenario And N

| scenario | N | alpha_c | 95% CI | width 10-90 | coverage | fit |
|---|---:|---:|---|---:|---|---|
| S3 | 500 | 0.0875 | [0.0875, 0.0875] | 0.0040 | crosses_0.5 | logistic_fit |
| S3 | 1000 | 0.0625 | [0.0625, 0.0625] | 0.0041 | crosses_0.5 | logistic_fit |
| S3 | 2000 | 0.0400 | [0.0400, 0.0400] | 0.0032 | crosses_0.5 | logistic_fit |
| S4 | 500 | 0.0241 | [0.0232, 0.0253] | 0.0130 | crosses_0.5 | logistic_fit |
| S4 | 1000 | 0.0226 | [0.0216, 0.0235] | 0.0112 | crosses_0.5 | logistic_fit |
| S4 | 2000 | 0.0225 | [0.0217, 0.0235] | 0.0082 | crosses_0.5 | logistic_fit |
