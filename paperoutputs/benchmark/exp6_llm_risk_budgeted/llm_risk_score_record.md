# WolfBench LLM Risk Score Record

Created: 2026-06-25T12:50:59Z

## Score Table

| Rank | Defense | TPS | DeltaAlphaC/W0 | CriticalDeltaP | CleanCost | FP | Source |
|---:|---|---:|---:|---:|---:|---:|---|
| 1 | qwen_risk | 23.96 | 4.9578 | -0.0833 | 0.0255 | 0.0000 | exp6_qwen14b_awq_risk_budgeted |
| 2 | deepseek_risk | 23.81 | 4.9578 | -0.0833 | 0.0248 | 0.0000 | exp6_deepseek_risk_budgeted |
| 3 | llama_risk | 20.63 | 2.2385 | 0.0833 | 0.0003 | 0.0000 | exp6_llama_risk_budgeted |
| 4 | mistral_risk | 1.02 | 4.9578 | -0.0833 | 0.1535 | 0.0000 | exp6_mistral_risk_budgeted |

## Run Notes

All artifacts are paper-facing benchmark outputs under paperoutputs/benchmark.
Legacy outputs/ runs are not used for this score record.

### exp6_qwen14b_awq_risk_budgeted

- requested_defenses: ['noguard', 'qwen_risk']
- scenarios: ['s1', 's2', 's3', 's4']
- n_grid: [1000]
- seeds: [1]

### exp6_deepseek_risk_budgeted

- requested_defenses: ['noguard', 'deepseek_risk']
- scenarios: ['s1', 's2', 's3', 's4']
- n_grid: [1000]
- seeds: [1]

### exp6_llama_risk_budgeted

- requested_defenses: ['noguard', 'llama_risk']
- scenarios: ['s1', 's2', 's3', 's4']
- n_grid: [1000]
- seeds: [1]

### exp6_mistral_risk_budgeted

- requested_defenses: ['noguard', 'mistral_risk']
- scenarios: ['s1', 's2', 's3', 's4']
- n_grid: [1000]
- seeds: [1]
