#!/usr/bin/env bash
set -euo pipefail

REPO=${REPO:-/root/WolfBench}
VENV=${VENV:-/root/autodl-tmp/venvs/vllm}
BENCH_ROOT="$REPO/paperoutputs/benchmark"
LOG_ROOT="$BENCH_ROOT/logs_openrouter_risk_budgeted"
SEEDS=${WOLFBENCH_EXP6_SEEDS:-1}
DEFENSES=${DEFENSES:-deepseek_risk,llama_risk,mistral_risk}
OPENROUTER_ENV_FILE=${OPENROUTER_ENV_FILE:-/root/.wolfbench/openrouter.env}

if [[ -z "${OPENROUTER_API_KEY:-}" && -z "${WOLFBENCH_OPENROUTER_API_KEY:-}" && -f "$OPENROUTER_ENV_FILE" ]]; then
  # shellcheck disable=SC1090
  source "$OPENROUTER_ENV_FILE"
fi

if [[ -z "${OPENROUTER_API_KEY:-}" && -z "${WOLFBENCH_OPENROUTER_API_KEY:-}" ]]; then
  echo "OPENROUTER_API_KEY is required for deepseek_risk/llama_risk/mistral_risk" >&2
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

IFS=',' read -r -a defense_array <<< "$DEFENSES"
outputs=()
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