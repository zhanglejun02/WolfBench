# WolfBench Exp6 Defense Leaderboard

N=[500, 1000, 2000], alpha_grids={'s1': [0.0, 0.0075, 0.01, 0.015, 0.02, 0.03], 's2': [0.0, 0.00025, 0.0005, 0.00075, 0.001, 0.0015, 0.0025], 's3': [0.0, 0.15, 0.3, 0.4, 0.5], 's4': [0.0, 0.01, 0.015, 0.02, 0.03, 0.05, 0.1, 0.15, 0.2]}, seeds=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50]

S1-S4 are mean raw DefenseScore values for each scenario, averaged across N. Avg ThresholdShift treats missing per-scenario threshold_shift values as 0.0.

| Defense model | S1 | S2 | S3 | S4 | Avg DefenseScore | Avg ThresholdShift | Worst Score |
|---|---:|---:|---:|---:|---:|---:|---:|
| random | -6.72 | 14.53 | -0.82 | -2.30 | 1.17 | -0.0024 | -6.72 |
| noguard | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.0000 | 0.00 |
| oracle | -2.11 | 0.04 | -0.78 | 1.78 | -0.27 | -0.0021 | -2.11 |
| rule | -13.57 | -0.01 | -1.69 | -17.44 | -8.18 | -0.0007 | -17.44 |
