#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
cd "${PROJECT_ROOT}"

CONFIG_PATH="${1:-configs/llamafactory/qwen25_7b_sft_lora.yaml}"
DATA_PATH="data/sft/v2_11k/medical_cot_sft_train.clean_10k_public.jsonl"
LOG_DIR="${LOG_DIR:-logs/train}"
RUN_ID="${RUN_ID:-$(basename "${CONFIG_PATH}" .yaml)-$(date +%Y%m%d-%H%M%S)}"
LOG_PATH="${LOG_PATH:-${LOG_DIR}/${RUN_ID}.log}"

if ! command -v llamafactory-cli >/dev/null 2>&1; then
  echo "ERROR: llamafactory-cli not found in PATH." >&2
  echo "Install/activate LLaMA-Factory, then rerun: bash scripts/train/run_sft_7b.sh" >&2
  exit 127
fi

if [[ ! -f "${DATA_PATH}" ]]; then
  echo "ERROR: missing SFT data file: ${DATA_PATH}" >&2
  exit 1
fi

mkdir -p "${LOG_DIR}"

echo "Using config: ${CONFIG_PATH}"
echo "Using data:   ${DATA_PATH} ($(wc -l < "${DATA_PATH}") rows)"
echo "Log file:     ${LOG_PATH}"
echo "Started at:   $(date)"
echo

PYTHONUNBUFFERED=1 \
HF_HUB_DISABLE_PROGRESS_BARS=0 \
llamafactory-cli train "${CONFIG_PATH}" 2>&1 | tee "${LOG_PATH}"

echo
echo "Finished at:  $(date)"
echo "Log file:     ${LOG_PATH}"
