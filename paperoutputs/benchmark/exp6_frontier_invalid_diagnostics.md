# Frontier Closed-Source Run Diagnostics

Created: 2026-06-25

## Status

The frontier closed-source run is invalid for leaderboard use.

The following defenses produced identical fallback-like scores and were diagnosed with direct OpenRouter smoke tests:

| Defense | Model | Smoke Result | Reason |
|---|---|---|---|
| claude_opus_risk | anthropic/claude-opus-4.8 | failed | OpenRouter 403: model is not available in your region |
| gemini25_pro_risk | google/gemini-2.5-pro | failed | OpenRouter 403: model is not available in your region |
| gpt41_risk | openai/gpt-4.1 | failed | OpenRouter 403: model is not available in your region |

Mistral was also diagnosed as invalid for OpenRouter use in this account/region:

| Defense | Model | Smoke Result | Reason |
|---|---|---|---|
| mistral_risk | mistralai/mistral-7b-instruct | failed | OpenRouter 404: no endpoints found |

## Root Cause

The benchmark was run with `WOLFBENCH_EXP6_LLM_STRICT=false` so that malformed JSON would not abort the entire run. This is useful for JSON formatting failures, but it also caused provider/model availability errors to be swallowed by the LLM backend. When every LLM call failed, `LLMRiskWolfGuardAgent` fell back to deterministic local `risk_features`, producing identical scores across unavailable models.

## Fix Applied

`paperoutputs/benchmark/scripts/run_openrouter_frontier_risk_budgeted.sh` now runs a strict JSON smoke test for each requested defense before starting the expensive Exp6 loop. If a model is unavailable or cannot return parseable JSON, the script fails before generating leaderboard artifacts.

## Leaderboard Policy

Do not use these frontier outputs as model performance evidence:

- `paperoutputs/benchmark/exp6_claude_opus_risk_budgeted`
- `paperoutputs/benchmark/exp6_gemini25_pro_risk_budgeted`
- `paperoutputs/benchmark/exp6_gpt41_risk_budgeted`

Use the refreshed `paperoutputs/benchmark/exp6_llm_risk_budgeted/llm_risk_score_record.*` official short-run table, which excludes the invalid frontier entries.
