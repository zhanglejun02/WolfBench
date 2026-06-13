# Paper Profile Run Status

Checked: 2026-06-09
Repo commit: `cf4d06c`
Hardware: CPU-only environment reported `GPU: No devices were found`.

## Completed

| Run | Status | Output directory | Notes |
|---|---|---|---|
| `exp2_society_size_scaling` | complete | `outputs/scaling_theory/exp2_society_size_scaling/` | 3,900 episodes, 50 seeds, summary written at `2026-06-09T07:51:44Z`. |
| `exp7_cross_mechanism_threshold` | complete | `outputs/scaling_theory/exp7_cross_mechanism_threshold/` | 5,100 episodes, 50 seeds, summary written at `2026-06-09T10:08:57Z`. S3/N=500 did not yield a logistic alpha_c on the current alpha grid. |
| `exp8_sensitivity_audit` | complete | `outputs/scaling_theory/exp8_sensitivity_audit/` | 4,400 episodes, 50 seeds, summary written at `2026-06-09T11:47:57Z`. |
| `exp6_defense_leaderboard` paper profile | complete | `outputs/defense_benchmark/exp6_paper50/` | 50 seeds, CPU-only built-in defense set, leaderboard written at `2026-06-09T19:54:54Z`. |

## Running

| Run | Status | Expected output directory | Notes |
|---|---|---|---|
| None | - | - | All CPU-only paper-profile runs requested in this pass are complete. |

## Current Process Check

`exp6_defense_leaderboard` completed with exit code 0. No GPU-backed Qwen/vLLM process was run because this machine reports `GPU: No devices were found`.