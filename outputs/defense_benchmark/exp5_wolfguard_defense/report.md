# Exp5 Defense Threshold-Shift Sweep

Scenarios: s1, s2
Defenses: noguard, rule, random
N grid: [1000]
Seeds: [1, 2, 3, 4, 5]
Alpha grids: {'s1': [0.0, 0.0075, 0.01, 0.0125, 0.015, 0.0175, 0.02, 0.025, 0.03], 's2': [0.0, 0.00025, 0.0005, 0.00075, 0.001, 0.0015, 0.002, 0.0025]}

| scenario | N | defense | alpha_c NoGuard | alpha_c defense | ThresholdShift | raw/bound shift | DefenseScore | Delta collapse | Utility | FP | Intervention |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| s1 | 1000 | noguard | 0.0175 | 0.0175 | 0.0000 | 0.0000 | 0.00 | 0.000 | 0.000 | 0.000 | 0.000 |
| s1 | 1000 | rule | 0.0175 | 0.0175 | 0.0000 | 0.0000 | -14.35 | 0.000 | 7.003 | 0.825 | 7.003 |
| s1 | 1000 | random | 0.0175 | 0.0175 | 0.0000 | 0.0000 | -2.30 | -0.067 | 0.370 | 0.000 | 0.370 |
| s2 | 1000 | noguard | 0.0008 | 0.0008 | 0.0000 | 0.0000 | 0.00 | 0.000 | 0.000 | 0.000 | 0.000 |
| s2 | 1000 | rule | 0.0008 | 0.0015 | 0.0008 | 0.0008 | 3.04 | 0.325 | 6.213 | 0.823 | 6.213 |
| s2 | 1000 | random | 0.0008 | 0.0015 | 0.0008 | 0.0008 | 15.53 | 0.325 | 0.370 | 0.000 | 0.370 |

Notes:
- ThresholdShift is alpha_c(defense) - alpha_c(NoGuard) when both critical points are observed inside the tested grid.
- raw/bound shift uses the conservative DefenseScore convention when a defense prevents collapse across the whole grid.
- Positive shifts mean the defense moved the critical harmful-agent ratio to the right.
