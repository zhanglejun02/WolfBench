# Qwen vLLM Baseline Analysis

Overall rank: 5 / 5
Mean DefenseScore: -12.49
Mean ThresholdShift: 0.0000
Mean CollapseRate: 0.500
Mean UtilityLoss: 5.102

## Deltas vs Baselines

| baseline | ΔDefenseScore | ΔCollapseRate | ΔUtilityLoss |
|---|---:|---:|---:|
| noguard | -12.49 | 0.167 | 5.102 |
| random | -17.56 | 0.167 | 4.732 |
| rule | -0.04 | 0.000 | -0.292 |
| oracle | -30.76 | 0.500 | 3.102 |

## Scenario Rows

| scenario | DefenseScore | CollapseRate | RetailLoss | UtilityLoss | ThresholdShift |
|---|---:|---:|---:|---:|---:|
| s1 | -7.43 | 0.667 | -0.0002 | 4.733 | 0.0000 |
| s2 | 11.99 | 0.667 | -0.0000 | 4.657 | 0.0000 |
| s3 | -5.90 | 0.000 | 0.0002 | 2.720 | 0.0000 |
| s4 | -48.62 | 0.667 | -0.0001 | 8.300 | 0.0000 |
