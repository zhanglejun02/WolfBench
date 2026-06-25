#!/usr/bin/env bash
set -euo pipefail

REPO=${REPO:-/root/WolfBench}
VENV=${VENV:-/root/autodl-tmp/venvs/vllm}
BENCH_ROOT="$REPO/paperoutputs/benchmark"
LOG_ROOT="$BENCH_ROOT/logs_openrouter_frontier_risk_budgeted"
OPENROUTER_ENV_FILE=${OPENROUTER_ENV_FILE:-/root/.wolfbench/openrouter.env}
SEEDS=${WOLFBENCH_EXP6_SEEDS:-1}
DEFENSES=${DEFENSES:-claude_opus_risk,gemini25_pro_risk,gpt41_risk}

if [[ -z "${OPENROUTER_API_KEY:-}" && -z "${WOLFBENCH_OPENROUTER_API_KEY:-}" && -f "$OPENROUTER_ENV_FILE" ]]; then
  # shellcheck disable=SC1090
  source "$OPENROUTER_ENV_FILE"
fi
if [[ -z "${OPENROUTER_API_KEY:-}" && -z "${WOLFBENCH_OPENROUTER_API_KEY:-}" ]]; then
  echo "OPENROUTER_API_KEY is required for frontier closed-source risk benchmark" >&2
  exit 2
fi
if [[ -z "${OPENROUTER_API_KEY:-}" && -n "${WOLFBENCH_OPENROUTER_API_KEY:-}" ]]; then
  export OPENROUTER_API_KEY="$WOLFBENCH_OPENROUTER_API_KEY"
fi

mkdir -p "$LOG_ROOT"
cd "$REPO"
source "$VENV/bin/activate"
export PYTHONPATH="$REPO:$REPO/src"
export PYTHONUNBUFFERED=1
export OMP_NUM_THREADS=${OMP_NUM_THREADS:-1}

smoke_model() {
  local defense="$1"
  echo "[$(date -Is)] smoke testing $defense"
  WOLFBENCH_SMOKE_DEFENSE="$defense" python - <<'PY'
from __future__ import annotations

import os
from wolfbench.defense import get_policy

defense = os.environ["WOLFBENCH_SMOKE_DEFENSE"]
policy = get_policy(defense, strict=True)
backend = getattr(policy, "backend", None)
if backend is None:
    raise SystemExit(f"{defense} did not create an LLM backend")
result = backend.chat_json(
    "Return JSON only. No markdown or explanation.",
    "Return exactly {\"ok\": true, \"score\": 0.5} as JSON.",
)
if result.get("ok") is not True:
    raise SystemExit(f"{defense} smoke returned unexpected JSON: {result!r}")
print(f"smoke ok: {defense} -> {getattr(backend, 'model', 'unknown')}")
PY
}

IFS=',' read -r -a defense_array <<< "$DEFENSES"
outputs=()
for defense in "${defense_array[@]}"; do
  defense="${defense// /}"
  [[ -z "$defense" ]] && continue
  smoke_model "$defense"
done

for defense in "${defense_array[@]}"; do
  defense="${defense// /}"
  [[ -z "$defense" ]] && continue
  out_name="exp6_${defense}_budgeted"
  outputs+=("$out_name")
  log_file="$LOG_ROOT/${defense}.log"
  echo "[$(date -Is)] running $defense into $out_name"
  WOLFBENCH_EXP6_OUT="$out_name" \
  WOLFBENCH_EXP6_DEFENSES="noguard,$defense" \
  WOLFBENCH_EXP6_UPPER_BOUNDS= \
  WOLFBENCH_EXP6_SCENARIOS=s1,s2,s3,s4 \
  WOLFBENCH_EXP6_N_GRID=1000 \
  WOLFBENCH_EXP6_SEEDS="$SEEDS" \
  WOLFBENCH_EXP6_ALPHAS_S1=0,0.01,0.015,0.02,0.03 \
  WOLFBENCH_EXP6_ALPHAS_S2=0,0.0005,0.00075,0.001,0.0015 \
  WOLFBENCH_EXP6_ALPHAS_S3=0,0.3,0.4,0.5 \
  WOLFBENCH_EXP6_ALPHAS_S4=0,0.01,0.015,0.02,0.03 \
  WOLFBENCH_EXP6_CI_BOOT=${WOLFBENCH_EXP6_CI_BOOT:-200} \
  WOLFBENCH_EXP6_LLM_STRICT=${WOLFBENCH_EXP6_LLM_STRICT:-false} \
  python -m experiments.defense_benchmark.exp6_defense_leaderboard \
    2>&1 | tee "$log_file"
done

"$BENCH_ROOT/scripts/summarize_llm_risk_scores.sh" "${outputs[@]}"

all_outputs=()
for name in \
  exp6_qwen14b_awq_risk_budgeted \
  exp6_deepseek_risk_budgeted \
  exp6_llama_risk_budgeted \
  exp6_mistral_risk_budgeted \
  "${outputs[@]}"; do
  if [[ -f "$BENCH_ROOT/$name/leaderboard.csv" ]]; then
    all_outputs+=("$name")
  fi
done
if [[ ${#all_outputs[@]} -gt 0 ]]; then
  "$BENCH_ROOT/scripts/summarize_llm_risk_scores.sh" "${all_outputs[@]}"
fi
