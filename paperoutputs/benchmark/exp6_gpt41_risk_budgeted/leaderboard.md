# WolfBench Exp6 Defense Leaderboard

N=[1000], alpha_grids={'s1': [0.0, 0.01, 0.015, 0.02, 0.03], 's2': [0.0, 0.0005, 0.00075, 0.001, 0.0015], 's3': [0.0, 0.3, 0.4, 0.5], 's4': [0.0, 0.01, 0.015, 0.02, 0.03]}, seeds=[1]

TPS is the official nonnegative leaderboard score. It rewards threshold protection in the NoGuard near-critical band and applies a clean-market cost gate.
RawNet and legacy DefenseScore remain diagnostic fields in CSV/JSON outputs. Competitive rank excludes controls and oracle upper bounds.

## Eligible Submissions

| Rank | Defense | Track | TPS ↑ | Δαc/W0 ↑ | Critical ΔP ↑ | CleanCost ↓ | FP ↓ | Status |
|---:|---|---|---:|---:|---:|---:|---:|---|
| 1 | gpt41_risk | open_llm_risk | 1.02 | 4.9578 | -0.0833 | 0.1535 | 0.0000 | eligible |

## Controls (Not Ranked)

| Rank | Defense | Track | TPS ↑ | Δαc/W0 ↑ | Critical ΔP ↑ | CleanCost ↓ | FP ↓ | Status |
|---:|---|---|---:|---:|---:|---:|---:|---|
| - | noguard | control | 0.00 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | reference |

## Threshold Table

| Defense | S1 alpha_c | S1 delta alpha_c | S2 alpha_c | S2 delta alpha_c |
|---|---:|---:|---:|---:|
| noguard | 0.0175 | 0.0000 | 0.0006 | 0.0000 |
| gpt41_risk | 0.0175 | 0.0000 | 0.0012 | 0.0006 |
