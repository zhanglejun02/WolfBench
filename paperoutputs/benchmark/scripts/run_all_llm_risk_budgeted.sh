#!/usr/bin/env bash
set -euo pipefail

REPO=${REPO:-/root/WolfBench}
BENCH_ROOT="$REPO/paperoutputs/benchmark"

"$BENCH_ROOT/scripts/run_qwen14b_awq_risk_budgeted.sh"

if [[ -n "${OPENROUTER_API_KEY:-}" || -n "${WOLFBENCH_OPENROUTER_API_KEY:-}" ]]; then
  "$BENCH_ROOT/scripts/run_openrouter_risk_budgeted.sh"
  "$BENCH_ROOT/scripts/summarize_llm_risk_scores.sh" \
    exp6_qwen14b_awq_risk_budgeted \
    exp6_deepseek_risk_budgeted \
    exp6_llama_risk_budgeted \
    exp6_mistral_risk_budgeted
else
  echo "OpenRouter key not set; wrote Qwen-only budgeted result."
fi