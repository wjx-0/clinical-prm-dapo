#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
cd "${PROJECT_ROOT}"

python eval/infer.py --split dev --output outputs/baseline/predictions.jsonl
python eval/metrics.py --predictions outputs/baseline/predictions.jsonl
