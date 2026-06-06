#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
cd "${PROJECT_ROOT}"

MODEL="${MODEL:-Qwen/Qwen2.5-7B-Instruct}"
BASE_URL="${BASE_URL:-http://127.0.0.1:8000/v1}"
API_KEY="${API_KEY:-EMPTY}"
SAMPLE_PER_FILE="${SAMPLE_PER_FILE:-200}"
WORKERS="${WORKERS:-4}"
MAX_TOKENS="${MAX_TOKENS:-512}"
TEMPERATURE="${TEMPERATURE:-0.0}"
TOP_P="${TOP_P:-1.0}"
PROGRESS_EVERY="${PROGRESS_EVERY:-10}"
RUN_NAME="${RUN_NAME:-qwen25_7b_base}"

python scripts/eval/eval_openai_mcqa.py \
  --data data/processed/medqa_dev.jsonl \
  --data data/processed/medmcqa_dev.jsonl \
  --model "${MODEL}" \
  --base-url "${BASE_URL}" \
  --api-key "${API_KEY}" \
  --sample-per-file "${SAMPLE_PER_FILE}" \
  --workers "${WORKERS}" \
  --max-tokens "${MAX_TOKENS}" \
  --temperature "${TEMPERATURE}" \
  --top-p "${TOP_P}" \
  --progress-every "${PROGRESS_EVERY}" \
  --output "outputs/eval/${RUN_NAME}_dev_predictions.jsonl" \
  --report "docs/${RUN_NAME}_dev_eval.md"
