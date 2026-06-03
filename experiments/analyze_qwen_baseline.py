"""Small post-run analysis for the exp6 Qwen/vLLM baseline."""
from __future__ import annotations

import csv
import json
from pathlib import Path


EXP6_DIR = Path(__file__).resolve().parent.parent / "outputs" / "exp6"


def _read_csv(path: Path) -> list[dict[str, str]]:
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def _float(row: dict[str, str], key: str) -> float:
    value = row.get(key, "")
    return float(value) if value not in {"", "None", "null"} else 0.0


def main() -> None:
    leaderboard_path = EXP6_DIR / "leaderboard.csv"
    overall_path = EXP6_DIR / "leaderboard_overall.csv"
    if not leaderboard_path.exists() or not overall_path.exists():
        raise FileNotFoundError("Run experiments.exp6_defense_leaderboard first.")

    leaderboard = _read_csv(leaderboard_path)
    overall = _read_csv(overall_path)
    by_defense = {row["defense"]: row for row in overall}
    if "qwen" not in by_defense:
        raise RuntimeError("The exp6 leaderboard does not contain a qwen row.")

    ordered = sorted(overall, key=lambda r: _float(r, "defense_score_mean"), reverse=True)
    qwen = by_defense["qwen"]
    qwen_rank = next(i for i, row in enumerate(ordered, 1) if row["defense"] == "qwen")
    comparisons = {}
    for baseline in ["noguard", "random", "rule", "oracle"]:
        if baseline in by_defense:
            comparisons[baseline] = {
                "defense_score_delta": (
                    _float(qwen, "defense_score_mean")
                    - _float(by_defense[baseline], "defense_score_mean")
                ),
                "collapse_rate_delta": (
                    _float(qwen, "collapse_rate_mean")
                    - _float(by_defense[baseline], "collapse_rate_mean")
                ),
                "utility_loss_delta": (
                    _float(qwen, "utility_loss_mean")
                    - _float(by_defense[baseline], "utility_loss_mean")
                ),
            }

    scenario_rows = [row for row in leaderboard if row["defense"] == "qwen"]
    analysis = {
        "qwen_rank": qwen_rank,
        "qwen_overall": qwen,
        "comparisons": comparisons,
        "qwen_by_scenario": scenario_rows,
    }
    (EXP6_DIR / "qwen_analysis.json").write_text(json.dumps(analysis, indent=2))

    lines = [
        "# Qwen vLLM Baseline Analysis",
        "",
        f"Overall rank: {qwen_rank} / {len(ordered)}",
        f"Mean DefenseScore: {_float(qwen, 'defense_score_mean'):.2f}",
        f"Mean ThresholdShift: {_float(qwen, 'threshold_shift_mean'):.4f}",
        f"Mean CollapseRate: {_float(qwen, 'collapse_rate_mean'):.3f}",
        f"Mean UtilityLoss: {_float(qwen, 'utility_loss_mean'):.3f}",
        "",
        "## Deltas vs Baselines",
        "",
        "| baseline | ΔDefenseScore | ΔCollapseRate | ΔUtilityLoss |",
        "|---|---:|---:|---:|",
    ]
    for baseline, vals in comparisons.items():
        lines.append(
            f"| {baseline} | {vals['defense_score_delta']:.2f} | "
            f"{vals['collapse_rate_delta']:.3f} | {vals['utility_loss_delta']:.3f} |"
        )
    lines.extend([
        "",
        "## Scenario Rows",
        "",
        "| scenario | DefenseScore | CollapseRate | RetailLoss | UtilityLoss | ThresholdShift |",
        "|---|---:|---:|---:|---:|---:|",
    ])
    for row in scenario_rows:
        lines.append(
            f"| {row['scenario']} | {_float(row, 'defense_score'):.2f} | "
            f"{_float(row, 'def_collapse_rate'):.3f} | "
            f"{_float(row, 'def_retail_loss'):.4f} | "
            f"{_float(row, 'utility_loss'):.3f} | "
            f"{_float(row, 'threshold_shift'):.4f} |"
        )
    (EXP6_DIR / "qwen_analysis.md").write_text("\n".join(lines) + "\n")
    print("Wrote", EXP6_DIR / "qwen_analysis.md")


if __name__ == "__main__":
    main()