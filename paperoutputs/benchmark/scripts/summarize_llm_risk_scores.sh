#!/usr/bin/env bash
set -euo pipefail

REPO=${REPO:-/root/WolfBench}
BENCH_ROOT="$REPO/paperoutputs/benchmark"

if [[ $# -lt 1 ]]; then
  echo "usage: $0 OUTPUT_NAME [OUTPUT_NAME ...]" >&2
  echo "example: $0 exp6_qwen14b_awq_risk_budgeted" >&2
  exit 2
fi

cd "$REPO"
export PYTHONPATH="$REPO:$REPO/src"

python - "$BENCH_ROOT" "$@" <<'PY'
from __future__ import annotations

import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

bench_root = Path(sys.argv[1])
names = sys.argv[2:]


def read_csv(path: Path) -> list[dict[str, str]]:
    with open(path, newline="") as handle:
        return list(csv.DictReader(handle))


def as_float(value: object, default: float = 0.0) -> float:
    try:
        if value in (None, "", "None", "none", "nan", "NaN"):
            return default
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default


def first(row: dict[str, str], *keys: str) -> str:
    for key in keys:
        if key in row and row[key] not in ("", None):
            return row[key]
    return ""


combined_rows: list[dict[str, object]] = []
details: dict[str, object] = {}
for name in names:
    out_dir = bench_root / name
    summary_path = out_dir / "summary.json"
    leaderboard_path = out_dir / "leaderboard.csv"
    scenario_path = out_dir / "leaderboard_by_scenario.csv"
    if not leaderboard_path.exists():
        raise FileNotFoundError(f"missing leaderboard.csv in {out_dir}")

    leaderboard = read_csv(leaderboard_path)
    scenario_rows = read_csv(scenario_path) if scenario_path.exists() else []
    summary = json.loads(summary_path.read_text()) if summary_path.exists() else {}
    for row in leaderboard:
        defense = first(row, "Defense", "defense", "Defense model")
        if not defense:
            continue
        combined_rows.append({
            "output": name,
            "defense": defense,
            "track": first(row, "Track", "track"),
            "status": first(row, "Status", "status"),
            "rank": first(row, "Rank", "rank"),
            "tps": as_float(first(row, "TPS", "tps_official_mean", "tps_mean")),
            "delta_alpha_c_over_w0": as_float(first(row, "DeltaAlphaC/W0", "delta_alpha_c_over_w0_mean")),
            "critical_delta_p": as_float(first(row, "CriticalDeltaP", "critical_band_delta_p_mean")),
            "clean_cost": as_float(first(row, "CleanCost", "clean_cost_index_mean")),
            "fp": as_float(first(row, "FP", "false_positive_rate_mean")),
        })
    details[name] = {
        "summary_path": str(summary_path),
        "leaderboard_path": str(leaderboard_path),
        "scenario_path": str(scenario_path),
        "requested_defenses": summary.get("requested_defenses", []),
        "defenses": summary.get("defenses", []),
        "scenarios": summary.get("scenarios", []),
        "alpha_grids": summary.get("alpha_grids", {}),
        "n_grid": summary.get("n_grid", []),
        "seeds": summary.get("seeds", []),
        "scenario_rows": scenario_rows,
    }

combined_rows.sort(key=lambda item: as_float(item.get("tps")), reverse=True)
for index, row in enumerate(combined_rows, 1):
    row["combined_rank"] = index

target_dir = bench_root / names[0] if len(names) == 1 else bench_root / "exp6_llm_risk_budgeted"
target_dir.mkdir(parents=True, exist_ok=True)

csv_path = target_dir / "llm_risk_score_record.csv"
with open(csv_path, "w", newline="") as handle:
    fieldnames = [
        "combined_rank", "output", "defense", "track", "status", "rank", "tps",
        "delta_alpha_c_over_w0", "critical_delta_p", "clean_cost", "fp",
    ]
    writer = csv.DictWriter(handle, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(combined_rows)

json_path = target_dir / "llm_risk_score_record.json"
json_path.write_text(json.dumps({
    "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
    "source_outputs": names,
    "rows": combined_rows,
    "details": details,
}, indent=2, default=str) + "\n")

md_path = target_dir / "llm_risk_score_record.md"
lines = [
    "# WolfBench LLM Risk Score Record",
    "",
    f"Created: {datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')}",
    "",
    "## Score Table",
    "",
    "| Rank | Defense | TPS | DeltaAlphaC/W0 | CriticalDeltaP | CleanCost | FP | Source |",
    "|---:|---|---:|---:|---:|---:|---:|---|",
]
for row in combined_rows:
    lines.append(
        f"| {row['combined_rank']} | {row['defense']} | {as_float(row['tps']):.2f} | "
        f"{as_float(row['delta_alpha_c_over_w0']):.4f} | {as_float(row['critical_delta_p']):.4f} | "
        f"{as_float(row['clean_cost']):.4f} | {as_float(row['fp']):.4f} | {row['output']} |"
    )
lines.extend([
    "",
    "## Run Notes",
    "",
    "All artifacts are paper-facing benchmark outputs under paperoutputs/benchmark.",
    "Legacy outputs/ runs are not used for this score record.",
])
for name, info in details.items():
    lines.extend([
        "",
        f"### {name}",
        "",
        f"- requested_defenses: {info.get('requested_defenses')}",
        f"- scenarios: {info.get('scenarios')}",
        f"- n_grid: {info.get('n_grid')}",
        f"- seeds: {info.get('seeds')}",
    ])
md_path.write_text("\n".join(lines) + "\n")

print(f"wrote {md_path}")
print(f"wrote {csv_path}")
print(f"wrote {json_path}")
PY