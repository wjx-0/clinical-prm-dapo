#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
cd "${PROJECT_ROOT}"

# TODO: Replace this with the exact verl GRPO entrypoint for your install.
python -m verl.trainer.main_ppo --config-path=configs/verl --config-name=grpo_medqa_3b
