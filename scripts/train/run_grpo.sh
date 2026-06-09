#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
cd "${PROJECT_ROOT}"

# First GRPO run for the 7B medical MCQA policy. Defaults train LoRA adapters
# on top of the merged SFT epoch1 model; smoke tests can override from shell.

MODEL_PATH="${MODEL_PATH:-${PROJECT_ROOT}/saves/qwen25-7b/merged/sft-v3_12866-train-prop-topup2866-ep1}"
TRAIN_FILES="${TRAIN_FILES:-${PROJECT_ROOT}/data/rl/v1_grpo_10k/train.parquet}"
VAL_FILES="${VAL_FILES:-${PROJECT_ROOT}/data/rl/v1_grpo_10k/val.parquet}"
REWARD_PATH="${REWARD_PATH:-${PROJECT_ROOT}/reward/total_reward.py}"
REWARD_PROFILE="${REWARD_PROFILE:-orm_v1}"
REWARD_CONFIG_PATH="${REWARD_CONFIG_PATH:-${PROJECT_ROOT}/configs/verl/reward_config.yaml}"
PRM_MODEL_PATH="${PRM_MODEL_PATH:-}"
OUTPUT_DIR="${OUTPUT_DIR:-${PROJECT_ROOT}/saves/qwen25-7b/grpo-lora/v1-medical-7b-ep1-init}"
PROJECT_NAME="${PROJECT_NAME:-clinical-prm-dapo}"
EXPERIMENT_NAME="${EXPERIMENT_NAME:-qwen25_7b_grpo_lora_v1_medical}"

N_GPUS="${N_GPUS:-1}"
ROLLOUT_TP="${ROLLOUT_TP:-${N_GPUS}}"
ROLLOUT_N="${ROLLOUT_N:-2}"
MAX_PROMPT_LENGTH="${MAX_PROMPT_LENGTH:-1024}"
MAX_RESPONSE_LENGTH="${MAX_RESPONSE_LENGTH:-256}"
TRAIN_BATCH_SIZE="${TRAIN_BATCH_SIZE:-4}"
PPO_MINI_BATCH_SIZE="${PPO_MINI_BATCH_SIZE:-1}"
MICRO_BATCH_SIZE="${MICRO_BATCH_SIZE:-1}"
LR="${LR:-3e-5}"
FSDP_MODEL_DTYPE="${FSDP_MODEL_DTYPE:-bf16}"
USE_KL_LOSS="${USE_KL_LOSS:-False}"
KL_COEF="${KL_COEF:-0.0}"
TOTAL_EPOCHS="${TOTAL_EPOCHS:-1}"
SAVE_FREQ="${SAVE_FREQ:-25}"
TEST_FREQ="${TEST_FREQ:-25}"
VAL_BEFORE_TRAIN="${VAL_BEFORE_TRAIN:-False}"
GPU_MEMORY_UTILIZATION="${GPU_MEMORY_UTILIZATION:-0.45}"
USE_REMOVE_PADDING="${USE_REMOVE_PADDING:-False}"
ATTN_IMPLEMENTATION="${ATTN_IMPLEMENTATION:-sdpa}"
ACTOR_PARAM_OFFLOAD="${ACTOR_PARAM_OFFLOAD:-True}"
ACTOR_OPTIMIZER_OFFLOAD="${ACTOR_OPTIMIZER_OFFLOAD:-True}"
REF_PARAM_OFFLOAD="${REF_PARAM_OFFLOAD:-True}"
REWARD_NUM_WORKERS="${REWARD_NUM_WORKERS:-1}"
AGENT_NUM_WORKERS="${AGENT_NUM_WORKERS:-1}"
DATALOADER_NUM_WORKERS="${DATALOADER_NUM_WORKERS:-0}"
LORA_RANK="${LORA_RANK:-8}"
LORA_ALPHA="${LORA_ALPHA:-16}"
LORA_TARGET_MODULES="${LORA_TARGET_MODULES:-all-linear}"
ROLLOUT_LOAD_FORMAT="${ROLLOUT_LOAD_FORMAT:-safetensors}"
ROLLOUT_MAX_MODEL_LEN="${ROLLOUT_MAX_MODEL_LEN:-$((MAX_PROMPT_LENGTH + MAX_RESPONSE_LENGTH))}"
ROLLOUT_MAX_NUM_SEQS="${ROLLOUT_MAX_NUM_SEQS:-4}"
ROLLOUT_MAX_NUM_BATCHED_TOKENS="${ROLLOUT_MAX_NUM_BATCHED_TOKENS:-1024}"
MODEL_USE_SHM="${MODEL_USE_SHM:-False}"
ROLLOUT_LAYERED_SUMMON="${ROLLOUT_LAYERED_SUMMON:-True}"
ROLLOUT_ENFORCE_EAGER="${ROLLOUT_ENFORCE_EAGER:-True}"
ROLLOUT_ENABLE_PREFIX_CACHING="${ROLLOUT_ENABLE_PREFIX_CACHING:-False}"

mkdir -p "${OUTPUT_DIR}" logs/train

export PYTHONPATH="${PROJECT_ROOT}:${PYTHONPATH:-}"
export TOKENIZERS_PARALLELISM="${TOKENIZERS_PARALLELISM:-false}"
export HYDRA_FULL_ERROR="${HYDRA_FULL_ERROR:-1}"
export REWARD_PROFILE
export REWARD_CONFIG_PATH
export PRM_MODEL_PATH
export VLLM_USE_V1="${VLLM_USE_V1:-0}"
export VLLM_WORKER_MULTIPROC_METHOD="${VLLM_WORKER_MULTIPROC_METHOD:-spawn}"

# vLLM's CuMemAllocator memory pool is incompatible with expandable_segments.
# Keep these unset for colocated rollout workers.
unset PYTORCH_CUDA_ALLOC_CONF
unset PYTORCH_ALLOC_CONF

python -m verl.trainer.main_ppo \
  algorithm.adv_estimator=grpo \
  algorithm.use_kl_in_reward=False \
  data.train_files="${TRAIN_FILES}" \
  data.val_files="${VAL_FILES}" \
  data.train_batch_size="${TRAIN_BATCH_SIZE}" \
  data.dataloader_num_workers="${DATALOADER_NUM_WORKERS}" \
  data.max_prompt_length="${MAX_PROMPT_LENGTH}" \
  data.max_response_length="${MAX_RESPONSE_LENGTH}" \
  actor_rollout_ref.model.path="${MODEL_PATH}" \
  actor_rollout_ref.model.use_remove_padding="${USE_REMOVE_PADDING}" \
  actor_rollout_ref.model.use_shm="${MODEL_USE_SHM}" \
  +actor_rollout_ref.model.override_config.attn_implementation="${ATTN_IMPLEMENTATION}" \
  +actor_rollout_ref.model.override_config._attn_implementation="${ATTN_IMPLEMENTATION}" \
  actor_rollout_ref.model.lora_rank="${LORA_RANK}" \
  actor_rollout_ref.model.lora_alpha="${LORA_ALPHA}" \
  actor_rollout_ref.model.target_modules="${LORA_TARGET_MODULES}" \
  actor_rollout_ref.actor.optim.lr="${LR}" \
  actor_rollout_ref.actor.use_kl_loss="${USE_KL_LOSS}" \
  actor_rollout_ref.actor.kl_loss_coef="${KL_COEF}" \
  actor_rollout_ref.actor.kl_loss_type=low_var_kl \
  actor_rollout_ref.actor.ppo_mini_batch_size="${PPO_MINI_BATCH_SIZE}" \
  actor_rollout_ref.actor.ppo_micro_batch_size_per_gpu="${MICRO_BATCH_SIZE}" \
  actor_rollout_ref.actor.use_remove_padding="${USE_REMOVE_PADDING}" \
  actor_rollout_ref.actor.fsdp_config.model_dtype="${FSDP_MODEL_DTYPE}" \
  actor_rollout_ref.actor.fsdp_config.param_offload="${ACTOR_PARAM_OFFLOAD}" \
  actor_rollout_ref.actor.fsdp_config.optimizer_offload="${ACTOR_OPTIMIZER_OFFLOAD}" \
  actor_rollout_ref.rollout.name=vllm \
  actor_rollout_ref.rollout.tensor_model_parallel_size="${ROLLOUT_TP}" \
  actor_rollout_ref.rollout.gpu_memory_utilization="${GPU_MEMORY_UTILIZATION}" \
  actor_rollout_ref.rollout.log_prob_micro_batch_size_per_gpu="${MICRO_BATCH_SIZE}" \
  actor_rollout_ref.rollout.load_format="${ROLLOUT_LOAD_FORMAT}" \
  actor_rollout_ref.rollout.max_model_len="${ROLLOUT_MAX_MODEL_LEN}" \
  actor_rollout_ref.rollout.max_num_seqs="${ROLLOUT_MAX_NUM_SEQS}" \
  actor_rollout_ref.rollout.max_num_batched_tokens="${ROLLOUT_MAX_NUM_BATCHED_TOKENS}" \
  actor_rollout_ref.rollout.layered_summon="${ROLLOUT_LAYERED_SUMMON}" \
  actor_rollout_ref.rollout.enforce_eager="${ROLLOUT_ENFORCE_EAGER}" \
  actor_rollout_ref.rollout.enable_prefix_caching="${ROLLOUT_ENABLE_PREFIX_CACHING}" \
  actor_rollout_ref.rollout.agent.num_workers="${AGENT_NUM_WORKERS}" \
  actor_rollout_ref.rollout.n="${ROLLOUT_N}" \
  actor_rollout_ref.ref.log_prob_micro_batch_size_per_gpu="${MICRO_BATCH_SIZE}" \
  actor_rollout_ref.ref.fsdp_config.model_dtype="${FSDP_MODEL_DTYPE}" \
  actor_rollout_ref.ref.fsdp_config.param_offload="${REF_PARAM_OFFLOAD}" \
  reward.reward_model.enable=False \
  reward.num_workers="${REWARD_NUM_WORKERS}" \
  reward.custom_reward_function.path="${REWARD_PATH}" \
  reward.custom_reward_function.name=compute_score \
  trainer.project_name="${PROJECT_NAME}" \
  trainer.experiment_name="${EXPERIMENT_NAME}" \
  trainer.n_gpus_per_node="${N_GPUS}" \
  trainer.nnodes=1 \
  trainer.default_local_dir="${OUTPUT_DIR}" \
  trainer.save_freq="${SAVE_FREQ}" \
  trainer.test_freq="${TEST_FREQ}" \
  trainer.total_epochs="${TOTAL_EPOCHS}" \
  trainer.val_before_train="${VAL_BEFORE_TRAIN}" \
  trainer.logger='["console"]'
