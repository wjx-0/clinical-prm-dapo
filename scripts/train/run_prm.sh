#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
cd "${PROJECT_ROOT}"

PRM_CONFIG="${PRM_CONFIG:-configs/llamafactory/qwen25_3b_prm_lora.yaml}"
PRM_DATA_DIR="${PRM_DATA_DIR:-data/prm/v1_12866_process_rm}"
REBUILD_PRM_DATA="${REBUILD_PRM_DATA:-0}"

if [[ "${REBUILD_PRM_DATA}" == "1" || ! -s "${PRM_DATA_DIR}/prm_pairwise_train.jsonl" ]]; then
  python scripts/data/build_prm_data.py --output-dir "${PRM_DATA_DIR}"
fi

llamafactory-cli train "${PRM_CONFIG}"
