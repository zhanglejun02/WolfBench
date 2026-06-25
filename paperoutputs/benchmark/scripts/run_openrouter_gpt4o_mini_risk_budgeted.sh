#!/usr/bin/env bash
set -euo pipefail

REPO=${REPO:-/root/WolfBench}
VENV=${VENV:-/root/autodl-tmp/venvs/vllm}
BENCH_ROOT="$REPO/paperoutputs/benchmark"
LOG_ROOT="$BENCH_ROOT/logs_openrouter_risk_budgeted"
OPENROUTER_ENV_FILE=${OPENROUTER_ENV_FILE:-/root/.wolfbench/openrouter.env}
OUT_NAME=${OUT_NAME:-exp6_gpt4o_mini_risk_budgeted}
DEFENSE=${DEFENSE:-gpt4o_mini_risk}
MODEL=${OPENROUTER_MODEL:-openai/gpt-4o-mini}
SEEDS=${WOLFBENCH_EXP6_SEEDS:-1}

if [[ -z "${OPENROUTER_API_KEY:-}" && -z "${WOLFBENCH_OPENROUTER_API_KEY:-}" && -f "$OPENROUTER_ENV_FILE" ]]; then
  # shellcheck disable=SC1090
  source "$OPENROUTER_ENV_FILE"
fi
if [[ -z "${OPENROUTER_API_KEY:-}" && -z "${WOLFBENCH_OPENROUTER_API_KEY:-}" ]]; then
  echo "OPENROUTER_API_KEY is required for $DEFENSE" >&2
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

log_file="$LOG_ROOT/${DEFENSE}.log"
echo "[$(date -Is)] running $DEFENSE ($MODEL) into $OUT_NAME"
WOLFBENCH_EXP6_OUT="$OUT_NAME" \
WOLFBENCH_EXP6_DEFENSES="noguard,$DEFENSE" \
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

"$BENCH_ROOT/scripts/summarize_llm_risk_scores.sh" "$OUT_NAME"
if [[ -d "$BENCH_ROOT/exp6_qwen14b_awq_risk_budgeted" && -d "$BENCH_ROOT/exp6_deepseek_risk_budgeted" && -d "$BENCH_ROOT/exp6_llama_risk_budgeted" && -d "$BENCH_ROOT/exp6_mistral_risk_budgeted" ]]; then
  "$BENCH_ROOT/scripts/summarize_llm_risk_scores.sh" \
    exp6_qwen14b_awq_risk_budgeted \
    exp6_deepseek_risk_budgeted \
    exp6_llama_risk_budgeted \
    exp6_mistral_risk_budgeted \
    "$OUT_NAME"
fi
