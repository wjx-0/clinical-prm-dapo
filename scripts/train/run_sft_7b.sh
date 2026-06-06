#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
cd "${PROJECT_ROOT}"

CONFIG_PATH="${1:-configs/llamafactory/qwen25_7b_sft_lora.yaml}"
DATA_PATH="data/sft/v2_11k/medical_cot_sft_train.clean_10k_public.jsonl"

if ! command -v llamafactory-cli >/dev/null 2>&1; then
  echo "ERROR: llamafactory-cli not found in PATH." >&2
  echo "Install/activate LLaMA-Factory, then rerun: bash scripts/train/run_sft_7b.sh" >&2
  exit 127
fi

if [[ ! -f "${DATA_PATH}" ]]; then
  echo "ERROR: missing SFT data file: ${DATA_PATH}" >&2
  exit 1
fi

echo "Using config: ${CONFIG_PATH}"
echo "Using data:   ${DATA_PATH}"
llamafactory-cli train "${CONFIG_PATH}"
