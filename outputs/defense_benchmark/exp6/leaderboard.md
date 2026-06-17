# WolfBench Exp6 Defense Leaderboard

N=[500, 1000, 2000], alpha_grids={'s1': [0.0, 0.0075, 0.01, 0.015, 0.02, 0.03], 's2': [0.0, 0.00025, 0.0005, 0.00075, 0.001, 0.0015, 0.0025], 's3': [0.0, 0.15, 0.3, 0.4, 0.5], 's4': [0.0, 0.01, 0.015, 0.02, 0.03, 0.05, 0.1, 0.15, 0.2]}, seeds=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30]

S1-S4 are mean raw DefenseScore values for each scenario, averaged across N. Avg ThresholdShift treats missing per-scenario threshold_shift values as 0.0.

| Defense model | S1 | S2 | S3 | S4 | Avg DefenseScore | Avg ThresholdShift | Worst Score |
|---|---:|---:|---:|---:|---:|---:|---:|
| random | -7.11 | 15.27 | -0.82 | -1.93 | 1.35 | -0.0024 | -7.11 |
| noguard | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.0000 | 0.00 |
| oracle | -4.35 | 0.05 | -0.78 | 2.14 | -0.73 | -0.0027 | -4.35 |
| rule | -13.53 | 0.61 | -1.41 | -17.60 | -7.98 | -0.0007 | -17.60 |
