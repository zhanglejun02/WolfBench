# WolfBench Baseline Score Record

Created: 2026-06-24

## Overall Scores

| Defense | Track | TPS | DeltaAlphaC/W0 | CriticalDeltaP | CleanCost | FP | Status |
|---|---|---:|---:|---:|---:|---:|---|
| noguard | control | 0.00 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | reference |
| oracle | oracle_upper_bound | 48.76 | 13.8162 | 0.2500 | 0.0000 | 0.0000 | upper bound |

## Scenario Scores

| Scenario | Defense | TPS | DeltaAlphaC/W0 | CriticalDeltaP | CleanCost | FP |
|---|---|---:|---:|---:|---:|---:|
| s1 | noguard | 0.00 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| s1 | oracle | 83.82 | 23.9367 | 0.3333 | 0.0000 | 0.0000 |
| s2 | noguard | 0.00 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| s2 | oracle | 96.63 | 31.3283 | 0.6667 | 0.0000 | 0.0000 |
| s3 | noguard | 0.00 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| s3 | oracle | 9.48 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| s4 | noguard | 0.00 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| s4 | oracle | 5.13 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |

## Run Notes

- Output directory: `paperoutputs/benchmark/exp6_noguard_oracle_budgeted`
- Scenarios: `s1,s2,s3,s4`
- N grid: `1000`
- Seeds: `1`
- Alpha grids match `exp6_qwen14b_awq_risk_budgeted` for direct comparison.
- `noguard` is a control/reference, not a ranked submission.
- `oracle` is an upper bound, not a ranked submission.
