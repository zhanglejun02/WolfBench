#!/usr/bin/env bash
set -euo pipefail

OPENROUTER_ENV_FILE=${OPENROUTER_ENV_FILE:-/root/.wolfbench/openrouter.env}
mkdir -p "$(dirname "$OPENROUTER_ENV_FILE")"
chmod 700 "$(dirname "$OPENROUTER_ENV_FILE")"

read -rsp "OpenRouter API key: " key
echo
if [[ -z "$key" ]]; then
  echo "empty key, not writing $OPENROUTER_ENV_FILE" >&2
  exit 2
fi

umask 077
tmp_file="${OPENROUTER_ENV_FILE}.tmp"
printf 'export OPENROUTER_API_KEY=%q\n' "$key" > "$tmp_file"
mv "$tmp_file" "$OPENROUTER_ENV_FILE"
chmod 600 "$OPENROUTER_ENV_FILE"
unset key
echo "wrote $OPENROUTER_ENV_FILE with mode 600"