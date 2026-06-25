# WolfBench Exp6 Defense Leaderboard

N=[100], alpha_grids={'s1': [0.0, 0.01, 0.02], 's2': [0.0, 0.0005, 0.001]}, seeds=[1]

TPS is the official nonnegative leaderboard score. It rewards threshold protection in the NoGuard near-critical band and applies a clean-market cost gate.
RawNet and legacy DefenseScore remain diagnostic fields in CSV/JSON outputs. Competitive rank excludes controls and oracle upper bounds.

## Eligible Submissions

| Rank | Defense | Track | TPS ↑ | Δαc/W0 ↑ | Critical ΔP ↑ | CleanCost ↓ | FP ↓ | Status |
|---:|---|---|---:|---:|---:|---:|---:|---|
| 1 | topology_aware | submission | 2.32 | 0.0000 | 0.0000 | 0.0030 | 0.0000 | eligible |
| 2 | rule | rule_baseline | 0.00 | 0.0000 | 0.0000 | 0.3907 | 1.0000 | weak |

## Controls (Not Ranked)

| Rank | Defense | Track | TPS ↑ | Δαc/W0 ↑ | Critical ΔP ↑ | CleanCost ↓ | FP ↓ | Status |
|---:|---|---|---:|---:|---:|---:|---:|---|
| - | noguard | control | 0.00 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | reference |
| - | random | control | 0.00 | 0.0000 | 0.0000 | 0.0247 | 0.0000 | ineligible |

## Upper Bounds (Not Ranked)

| Rank | Defense | Track | TPS ↑ | Δαc/W0 ↑ | Critical ΔP ↑ | CleanCost ↓ | FP ↓ | Status |
|---:|---|---|---:|---:|---:|---:|---:|---|
| - | oracle | oracle_upper_bound | 1.51 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | upper bound |

## Threshold Table

| Defense | S1 alpha_c | S1 delta alpha_c | S2 alpha_c | S2 delta alpha_c |
|---|---:|---:|---:|---:|
| noguard | 0.0200 | 0.0000 | 0.0010 | 0.0000 |
| random | 0.0200 | 0.0000 | 0.0010 | 0.0000 |
| rule | 0.0200 | 0.0000 | 0.0010 | 0.0000 |
| topology_aware | 0.0200 | 0.0000 | 0.0010 | 0.0000 |
| oracle | 0.0200 | 0.0000 | 0.0010 | 0.0000 |
