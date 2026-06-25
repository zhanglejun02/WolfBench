#!/usr/bin/env bash
set -euo pipefail

REPO=${REPO:-/root/WolfBench}
VENV=${VENV:-/root/autodl-tmp/venvs/vllm}
MODEL_PATH=${MODEL_PATH:-/root/autodl-tmp/modelscope-cache/models/Qwen/Qwen3-14B-AWQ}
MODEL_ID=${MODEL_ID:-$MODEL_PATH}
SERVED_MODEL=${SERVED_MODEL:-qwen3-14b-awq}
HOST=${HOST:-127.0.0.1}
PORT=${PORT:-8000}
BASE_URL=${BASE_URL:-http://$HOST:$PORT/v1}
VLLM_SESSION=${VLLM_SESSION:-wolfbench_vllm_qwen14b_awq}
RUN_SESSION=${RUN_SESSION:-wolfbench_qwen14b_awq_risk_budgeted}
OUT_NAME=${OUT_NAME:-exp6_qwen14b_awq_risk_budgeted}
BENCH_ROOT="$REPO/paperoutputs/benchmark"
OUT_DIR="$BENCH_ROOT/$OUT_NAME"
LOG_DIR="$OUT_DIR/logs"
SEEDS=${WOLFBENCH_EXP6_SEEDS:-1}
VLLM_QUANTIZATION=${VLLM_QUANTIZATION:-awq_marlin}

mkdir -p "$LOG_DIR"
cd "$REPO"
source "$VENV/bin/activate"
export PYTHONPATH="$REPO:$REPO/src"
export PYTHONUNBUFFERED=1
export OMP_NUM_THREADS=${OMP_NUM_THREADS:-1}
export VLLM_USE_MODELSCOPE=${VLLM_USE_MODELSCOPE:-True}
export MODELSCOPE_CACHE=${MODELSCOPE_CACHE:-/root/autodl-tmp/modelscope-cache}
export HF_HOME=${HF_HOME:-/root/autodl-tmp/hf-cache}
export WOLFBENCH_VLLM_MODEL="$SERVED_MODEL"
export WOLFBENCH_VLLM_BASE_URL="$BASE_URL"
export WOLFBENCH_VLLM_API_KEY=${WOLFBENCH_VLLM_API_KEY:-EMPTY}

log() {
  echo "[$(date -Is)] $*"
}

start_vllm_if_needed() {
  if python - "$BASE_URL" "$SERVED_MODEL" <<'PY'
import json
import sys
import urllib.request

base_url, served_model = sys.argv[1], sys.argv[2]
try:
    with urllib.request.urlopen(base_url.rstrip("/") + "/models", timeout=5) as response:
        payload = json.loads(response.read().decode("utf-8"))
except Exception:
    raise SystemExit(1)
models = payload.get("data", []) if isinstance(payload, dict) else []
ids = {str(item.get("id", "")) for item in models if isinstance(item, dict)}
raise SystemExit(0 if served_model in ids else 1)
PY
  then
    log "vLLM already serving $SERVED_MODEL at $BASE_URL"
    return
  fi

  log "starting vLLM server for $SERVED_MODEL in tmux session $VLLM_SESSION"
  tmux kill-session -t "$VLLM_SESSION" 2>/dev/null || true
  tmux new-session -d -s "$VLLM_SESSION" \
    "source '$VENV/bin/activate' && export OMP_NUM_THREADS=1 VLLM_USE_MODELSCOPE=True MODELSCOPE_CACHE='$MODELSCOPE_CACHE' HF_HOME='$HF_HOME' && vllm serve '$MODEL_ID' --served-model-name '$SERVED_MODEL' --host '$HOST' --port '$PORT' --dtype auto --gpu-memory-utilization 0.90 --max-model-len 4096 --quantization '$VLLM_QUANTIZATION' --disable-log-requests 2>&1 | tee '$LOG_DIR/vllm_qwen14b_awq_server.log'"

  log "waiting for vLLM /v1/models endpoint"
  for _ in $(seq 1 240); do
    if python - "$BASE_URL" "$SERVED_MODEL" <<'PY'
import json
import sys
import urllib.request

base_url, served_model = sys.argv[1], sys.argv[2]
try:
    with urllib.request.urlopen(base_url.rstrip("/") + "/models", timeout=5) as response:
        payload = json.loads(response.read().decode("utf-8"))
except Exception:
    raise SystemExit(1)
models = payload.get("data", []) if isinstance(payload, dict) else []
ids = {str(item.get("id", "")) for item in models if isinstance(item, dict)}
raise SystemExit(0 if served_model in ids else 1)
PY
    then
      log "vLLM is ready"
      return
    fi
    sleep 10
  done
  log "vLLM did not become ready in time"
  exit 1
}

json_smoke() {
  log "running JSON smoke request against $SERVED_MODEL"
  python - <<'PY'
import os
from openai import OpenAI

client = OpenAI(base_url=os.environ["WOLFBENCH_VLLM_BASE_URL"], api_key=os.environ.get("WOLFBENCH_VLLM_API_KEY", "EMPTY"))
resp = client.chat.completions.create(
    model=os.environ["WOLFBENCH_VLLM_MODEL"],
    temperature=0.0,
    max_tokens=32,
    response_format={"type": "json_object"},
    extra_body={"chat_template_kwargs": {"enable_thinking": False}},
    messages=[
        {"role": "system", "content": "Return JSON only."},
        {"role": "user", "content": "Return {\"ok\": true}."},
    ],
)
content = resp.choices[0].message.content or "{}"
print(content)
if "ok" not in content:
    raise SystemExit("smoke response did not include ok")
PY
}

run_budgeted() {
  log "running Qwen14-AWQ qwen_risk budgeted leaderboard into $OUT_DIR"
  WOLFBENCH_EXP6_OUT="$OUT_NAME" \
  WOLFBENCH_EXP6_DEFENSES=noguard,qwen_risk \
  WOLFBENCH_EXP6_UPPER_BOUNDS= \
  WOLFBENCH_EXP6_SCENARIOS=s1,s2,s3,s4 \
  WOLFBENCH_EXP6_N_GRID=1000 \
  WOLFBENCH_EXP6_SEEDS="$SEEDS" \
  WOLFBENCH_EXP6_ALPHAS_S1=0,0.01,0.015,0.02,0.03 \
  WOLFBENCH_EXP6_ALPHAS_S2=0,0.0005,0.00075,0.001,0.0015 \
  WOLFBENCH_EXP6_ALPHAS_S3=0,0.3,0.4,0.5 \
  WOLFBENCH_EXP6_ALPHAS_S4=0,0.01,0.015,0.02,0.03 \
  WOLFBENCH_EXP6_CI_BOOT=${WOLFBENCH_EXP6_CI_BOOT:-200} \
  WOLFBENCH_EXP6_LLM_PROVIDER=vllm \
  WOLFBENCH_EXP6_LLM_MODEL="$SERVED_MODEL" \
  WOLFBENCH_EXP6_LLM_BASE_URL="$BASE_URL" \
  WOLFBENCH_EXP6_LLM_API_KEY=EMPTY \
  WOLFBENCH_EXP6_LLM_STRICT=true \
  python -m experiments.defense_benchmark.exp6_defense_leaderboard \
    2>&1 | tee "$LOG_DIR/qwen14b_awq_risk_budgeted.log"
}

log "Qwen14-AWQ risk budgeted runner starting"
start_vllm_if_needed
json_smoke
run_budgeted
"$BENCH_ROOT/scripts/summarize_llm_risk_scores.sh" "$OUT_NAME" 2>&1 | tee "$LOG_DIR/qwen14b_awq_risk_summary.log"
log "Qwen14-AWQ risk budgeted runner finished"