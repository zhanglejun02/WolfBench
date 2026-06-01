# WolfBench Exp6 Baseline Leaderboard

N=1000, alphas=[0.0, 0.005, 0.01, 0.02, 0.05, 0.1], seeds=[1, 2, 3, 4, 5]

| rank | defense | DefenseScore mean | std | mean ThresholdShift | mean CollapseRate | mean UtilityLoss | mean FP |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | random | 4.44 | 9.90 | 0.0000 | 0.450 | 0.370 | 0.000 |
| 2 | noguard | 0.00 | 0.00 | 0.0000 | 0.408 | 0.000 | 0.000 |
| 3 | oracle | 0.00 | 0.00 | 0.0000 | 0.408 | 0.000 | 0.000 |
| 4 | rule | -19.43 | 21.23 | 0.0000 | 0.500 | 5.381 | 479.326 |
