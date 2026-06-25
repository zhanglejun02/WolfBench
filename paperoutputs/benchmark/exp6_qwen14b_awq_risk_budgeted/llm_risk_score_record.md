# WolfBench LLM Risk Score Record

Created: 2026-06-24T06:57:54Z

## Score Table

| Rank | Defense | TPS | DeltaAlphaC/W0 | CriticalDeltaP | CleanCost | FP | Source |
|---:|---|---:|---:|---:|---:|---:|---|
| 1 | qwen_risk | 23.96 | 4.9578 | -0.0833 | 0.0255 | 0.0000 | exp6_qwen14b_awq_risk_budgeted |

## Run Notes

All artifacts are paper-facing benchmark outputs under paperoutputs/benchmark.
Legacy outputs/ runs are not used for this score record.

### exp6_qwen14b_awq_risk_budgeted

- requested_defenses: ['noguard', 'qwen_risk']
- scenarios: ['s1', 's2', 's3', 's4']
- n_grid: [1000]
- seeds: [1]
