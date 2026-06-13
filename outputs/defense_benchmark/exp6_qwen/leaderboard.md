# WolfBench Exp6 Baseline Leaderboard

N=[500, 1000, 2000], alpha_grids={'s1': [0.0, 0.0075, 0.01, 0.015, 0.02, 0.03], 's2': [0.0, 0.00025, 0.0005, 0.00075, 0.001, 0.0015, 0.0025], 's3': [0.0, 0.15, 0.3, 0.4, 0.5], 's4': [0.0, 0.01, 0.015, 0.02, 0.03, 0.05, 0.1, 0.15, 0.2]}, seeds=[1, 2, 3, 4, 5]

Control tracks are diagnostic only: their official score is capped at 0 while raw DefenseScore is still reported.

| rank | track | defense | OfficialScore mean | 95% CI | raw DefenseScore mean | raw 95% CI | mean ThresholdShift | mean CollapseRate | mean UtilityLoss | mean FP |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | control | noguard | 0.00 | [0.00, 0.00] | 0.00 | [0.00, 0.00] | 0.0000 | 0.383 | 0.000 | 0.000 |
| 2 | llm_from_scratch | qwen | -11.20 | [-17.93, -5.14] | -11.20 | [-17.93, -5.14] | -0.0141 | 0.411 | 5.100 | 0.596 |
