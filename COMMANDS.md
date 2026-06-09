# 常用命令备忘录

这份文件记录服务器上常用的 SFT、vLLM LoRA 部署和测评命令。默认项目路径：

```bash
cd ~/rivermind-data/repos/clinical-prm-dapo
```

## 1. 跑 SFT

当前 12866 clean 数据配置在：

```text
configs/llamafactory/qwen25_7b_sft_lora.yaml
```

直接训练：

```bash
cd ~/rivermind-data/repos/clinical-prm-dapo

llamafactory-cli train configs/llamafactory/qwen25_7b_sft_lora.yaml
```

后台训练并保存日志：

```bash
conda activate llamafactory
cd ~/rivermind-data/repos/clinical-prm-dapo
mkdir -p logs/train

nohup llamafactory-cli train configs/llamafactory/qwen25_7b_sft_lora.yaml \
  > logs/train/qwen25_7b_sft_v3_12866.log 2>&1 &

echo $! > logs/train/qwen25_7b_sft_v3_12866.pid
tail -f logs/train/qwen25_7b_sft_v3_12866.log
```

如果要跑 2 epoch，改 YAML 里两处：

```yaml
output_dir: saves/qwen25-7b/lora/sft-v3_12866-train-prop-topup2866-ep2
num_train_epochs: 2.0
```

说明：

- `output_dir` 一定要换新目录，避免覆盖 1 epoch 的 LoRA。
- `num_train_epochs` 控制训练轮数。
- 当前数据集是 `data/sft/v3_12866_train_prop_topup2866`，总数 12866 条。

## 2. 合并 epoch1 LoRA

GRPO 建议先用 epoch1 SFT 作为初始化模型。为了让 verl 直接读取完整 HF 模型，先把 base model 和 LoRA 合并。

合并配置：

```text
configs/llamafactory/qwen25_7b_merge_v3_12866_ep1.yaml
```

先确认 base model 和 LoRA 都在：

```bash
cd ~/rivermind-data/repos/clinical-prm-dapo

ls /root/rivermind-data/models/Qwen2.5-7B-Instruct
ls saves/qwen25-7b/lora/sft-v3_12866-train-prop-topup2866
```

执行合并：

```bash
conda activate llamafactory
cd ~/rivermind-data/repos/clinical-prm-dapo

llamafactory-cli export configs/llamafactory/qwen25_7b_merge_v3_12866_ep1.yaml
```

合并后输出目录：

```text
saves/qwen25-7b/merged/sft-v3_12866-train-prop-topup2866-ep1
```

检查文件：

```bash
ls -lh saves/qwen25-7b/merged/sft-v3_12866-train-prop-topup2866-ep1
```

说明：

- 合并后会多占大约 15-16GB 磁盘。
- 这个 merged 模型后面给 verl / GRPO 用。
- 如果只是 vLLM 测评，可以不合并，继续用 base + LoRA。

## 3. 停 vLLM

如果之前保存了 pid：

```bash
cd ~/rivermind-data/repos/clinical-prm-dapo
kill $(cat logs/eval/vllm_sft_v3_12866_lora.pid)
```

如果没停掉：

```bash
ps aux | grep vllm
kill -9 PID
```


## 4. 启动 vLLM LoRA 服务

不 merge，直接用 base model + LoRA adapter 部署。

```bash
conda activate vllm
cd ~/rivermind-data/repos/clinical-prm-dapo
mkdir -p logs/eval

unset LD_LIBRARY_PATH
unset LIBRARY_PATH

export CUDA_HOME="$CONDA_PREFIX"
export PATH="$CUDA_HOME/bin:$PATH"
export LD_LIBRARY_PATH="$CONDA_PREFIX/lib:$CONDA_PREFIX/lib64:/usr/lib/x86_64-linux-gnu"
export LIBRARY_PATH="$CONDA_PREFIX/lib:$CONDA_PREFIX/lib64:/usr/lib/x86_64-linux-gnu"

MODEL_DIR=/root/rivermind-data/models/Qwen2.5-7B-Instruct
LORA_DIR=saves/qwen25-7b/lora/sft-v3_12866-train-prop-topup2866

CUDA_VISIBLE_DEVICES=0 nohup vllm serve "$MODEL_DIR" \
  --served-model-name Qwen/Qwen2.5-7B-Instruct \
  --enable-lora \
  --lora-modules qwen25_7b_sft_v3_12866="$LORA_DIR" \
  --max-lora-rank 64 \
  --host 0.0.0.0 \
  --port 8000 \
  --dtype float16 \
  --max-model-len 4096 \
  --gpu-memory-utilization 0.92 \
  --max-num-seqs 64 \
  --max-num-batched-tokens 32768 \
  --enforce-eager \
  > logs/eval/vllm_sft_v3_12866_lora.log 2>&1 &

echo $! > logs/eval/vllm_sft_v3_12866_lora.pid
tail -f logs/eval/vllm_sft_v3_12866_lora.log
```


如果是 2 epoch，把这两处改掉：

```bash
LORA_DIR=saves/qwen25-7b/lora/sft-v3_12866-train-prop-topup2866-ep2
--lora-modules qwen25_7b_sft_v3_12866_ep2="$LORA_DIR"
```

说明：

- `--enable-lora`：让 vLLM 支持 LoRA adapter。
- `--lora-modules 名字=路径`：给 LoRA 起一个 OpenAI API 里使用的模型名。
- `--gpu-memory-utilization 0.92`：允许 vLLM 使用更多显存作为 KV cache。
- `--max-num-seqs 64`：最多同时处理 64 个请求序列。
- `--max-num-batched-tokens 32768`：一次调度最多合批这么多 token。
- 48G 显存可以先用这组参数；如果 OOM，把 `0.92` 降到 `0.88`。

检查服务：

```bash
curl http://127.0.0.1:8000/v1/models
```

应该能看到 LoRA 模型名，比如：

```text
qwen25_7b_sft_v3_12866
```

## 5. 跑 MedQA + MedMCQA dev 测评

全量测评：

```bash

cd ~/rivermind-data/repos/clinical-prm-dapo

MODEL=qwen25_7b_sft_v3_12866_ep2 \
BASE_URL=http://127.0.0.1:8000/v1 \
API_KEY=EMPTY \
SAMPLE_PER_FILE=0 \
WORKERS=64 \
MAX_TOKENS=768 \
RUN_NAME=qwen25_7b_sft_v3_12866_ep2 \
bash scripts/eval/eval_sft_openai.sh
```


如果测 2 epoch，把模型名和 run name 换掉：

```bash
MODEL=qwen25_7b_sft_v3_12866_ep2
RUN_NAME=qwen25_7b_sft_v3_12866_ep2
```

输出位置：

```text
outputs/eval/${RUN_NAME}_dev_predictions.jsonl
docs/${RUN_NAME}_dev_eval.md
```

说明：

- `SAMPLE_PER_FILE=0`：每个 dev 文件全量测评。
- `SAMPLE_PER_FILE=200`：每个 dev 文件抽 200 条，适合先检查服务。
- `WORKERS`：评测脚本并发请求数，48G 单卡可以先用 16，稳了再试 24。
- `MAX_TOKENS=768`：模型最多生成 768 token。

## 6. 常用检查命令

看训练数据行数：

```bash
wc -l data/sft/v3_12866_train_prop_topup2866/medical_cot_sft_train.clean_13k_public.jsonl
```

看 vLLM 日志：

```bash
tail -f logs/eval/vllm_sft_v3_12866_lora.log
```

看训练日志：

```bash
tail -f logs/train/qwen25_7b_sft_v3_12866.log
```

看显卡：

```bash
nvidia-smi
```

看评测结果：

```bash
cat docs/qwen25_7b_sft_v3_12866_dev_eval.md
```

## 7. 第一版 GRPO 数据准备

第一版 GRPO 先做难度采样数据，不直接全量上 train。流程是：

```text
1. 从 MedQA/MedMCQA train 构造 20000 条候选池
2. 用 epoch1 SFT LoRA 对每题采样 4 次，统计答对几次
3. 优先选 1/4、2/4、3/4 的题，生成 10000 train + 500 val 的 verl parquet
```

候选池本地已经生成过。如果服务器没有这个文件，可以重新生成：

```bash
conda activate vllm
cd ~/rivermind-data/repos/clinical-prm-dapo

python3 scripts/data/build_grpo_difficulty_data.py build-candidates
```

输出：

```text
data/rl/v1_grpo_10k/difficulty_candidate_pool.jsonl
docs/rl_v1_grpo_10k_candidate_pool.md
```

注意：难度采样要用 epoch1 LoRA 服务，不用 ep2。先启动 epoch1 vLLM，并确认模型名：

```bash
curl http://127.0.0.1:8000/v1/models
```

应该能看到：

```text
qwen25_7b_sft_v3_12866
```

先跑 100 条 smoke：

```bash
conda activate vllm
cd ~/rivermind-data/repos/clinical-prm-dapo

python3 scripts/data/build_grpo_difficulty_data.py sample-difficulty \
  --candidate-input data/rl/v1_grpo_10k/difficulty_candidate_pool.jsonl \
  --output data/rl/v1_grpo_10k/difficulty_samples_smoke.jsonl \
  --report-path docs/rl_v1_grpo_10k_difficulty_sampling_smoke.md \
  --model qwen25_7b_sft_v3_12866 \
  --base-url http://127.0.0.1:8000/v1 \
  --api-key EMPTY \
  --num-generations 4 \
  --workers 4 \
  --temperature 0.7 \
  --top-p 0.95 \
  --max-tokens 768 \
  --max-rows 100 \
  --resume \
  --progress-every 10
```

如果 smoke 没有大量 error，再跑完整 20000 条：

```bash
python3 scripts/data/build_grpo_difficulty_data.py sample-difficulty \
  --candidate-input data/rl/v1_grpo_10k/difficulty_candidate_pool.jsonl \
  --output data/rl/v1_grpo_10k/difficulty_samples_epoch1_n4.jsonl \
  --report-path docs/rl_v1_grpo_10k_difficulty_sampling.md \
  --model qwen25_7b_sft_v3_12866 \
  --base-url http://127.0.0.1:8000/v1 \
  --api-key EMPTY \
  --num-generations 4 \
  --workers 16 \
  --temperature 0.7 \
  --top-p 0.95 \
  --max-tokens 768 \
  --resume \
  --progress-every 50
```

说明：

- `--num-generations 4`：每道题生成 4 个回答。
- `correct_count=0/4` 是困难题，`4/4` 是简单题，`1/4-3/4` 是 GRPO 最有学习信号的题。
- `--resume`：中断后可以续跑，已经写入 output 的 id 会跳过。
- `--workers 16`：并发请求数。服务不稳就降到 8，吞吐不够再升到 32。

采样完成后，选出第一版 GRPO 数据：

```bash
python3 scripts/data/build_grpo_difficulty_data.py select-grpo \
  --difficulty-input data/rl/v1_grpo_10k/difficulty_samples_epoch1_n4.jsonl \
  --output-dir data/rl/v1_grpo_10k \
  --report-path docs/rl_v1_grpo_10k_selection.md \
  --train-size 10000 \
  --val-size 500 \
  --medqa-train-size 4000 \
  --medmcqa-train-size 6000
```

输出：

```text
data/rl/v1_grpo_10k/train.parquet
data/rl/v1_grpo_10k/val.parquet
data/rl/v1_grpo_10k/train.jsonl
data/rl/v1_grpo_10k/val.jsonl
data/rl/v1_grpo_10k/selected_debug.jsonl
docs/rl_v1_grpo_10k_selection.md
```

## 8. 第一版 GRPO-LoRA 训练

训练前确认三件事：

```bash
cd ~/rivermind-data/repos/clinical-prm-dapo

ls saves/qwen25-7b/merged/sft-v3_12866-train-prop-topup2866-ep1
ls data/rl/v1_grpo_10k/train.parquet
ls data/rl/v1_grpo_10k/val.parquet
```

先跑 LoRA smoke。这个只跑很小 batch，用来确认 verl、reward、数据、显存都没问题：

```bash
conda activate verl
cd ~/rivermind-data/repos/clinical-prm-dapo

CUDA_VISIBLE_DEVICES=0 \
USE_REMOVE_PADDING=False \
ATTN_IMPLEMENTATION=sdpa \
LORA_RANK=16 \
LORA_ALPHA=32 \
TRAIN_BATCH_SIZE=2 \
PPO_MINI_BATCH_SIZE=2 \
MICRO_BATCH_SIZE=1 \
MAX_PROMPT_LENGTH=1024 \
MAX_RESPONSE_LENGTH=128 \
ROLLOUT_N=2 \
GPU_MEMORY_UTILIZATION=0.20 \
TOTAL_EPOCHS=1 \
SAVE_FREQ=1000 \
TEST_FREQ=1000 \
bash scripts/train/run_grpo.sh
```

如果 smoke 能正常开始 rollout / train，再跑第一版正式训练：

```bash
conda activate verl
cd ~/rivermind-data/repos/clinical-prm-dapo

CUDA_VISIBLE_DEVICES=0 \
N_GPUS=1 \
ROLLOUT_TP=1 \
USE_REMOVE_PADDING=False \
ATTN_IMPLEMENTATION=sdpa \
LORA_RANK=16 \
LORA_ALPHA=32 \
TRAIN_BATCH_SIZE=16 \
PPO_MINI_BATCH_SIZE=8 \
MICRO_BATCH_SIZE=1 \
ROLLOUT_N=4 \
MAX_PROMPT_LENGTH=2048 \
MAX_RESPONSE_LENGTH=384 \
GPU_MEMORY_UTILIZATION=0.35 \
KL_COEF=0.002 \
TOTAL_EPOCHS=1 \
SAVE_FREQ=25 \
TEST_FREQ=25 \
bash scripts/train/run_grpo.sh
```

双 24G 多卡可以这样启动：

```bash
conda activate verl
cd ~/rivermind-data/repos/clinical-prm-dapo

CUDA_VISIBLE_DEVICES=0,1 \
N_GPUS=2 \
ROLLOUT_TP=2 \
USE_REMOVE_PADDING=False \
ATTN_IMPLEMENTATION=sdpa \
LORA_RANK=16 \
LORA_ALPHA=32 \
TRAIN_BATCH_SIZE=32 \
PPO_MINI_BATCH_SIZE=16 \
MICRO_BATCH_SIZE=1 \
ROLLOUT_N=4 \
MAX_PROMPT_LENGTH=2048 \
MAX_RESPONSE_LENGTH=384 \
GPU_MEMORY_UTILIZATION=0.35 \
TOTAL_EPOCHS=1 \
bash scripts/train/run_grpo.sh
```

输出目录默认是：

```text
saves/qwen25-7b/grpo-lora/v1-medical-7b-ep1-init
```

说明：

- 初始化模型是 epoch1 merged model。
- 这一版是 GRPO-LoRA，不是 full-parameter GRPO。
- LoRA 默认 `rank=16, alpha=32, target_modules=all-linear`。
- reward 入口是 `reward/total_reward.py`，会抽 `<answer>A</answer>` 里的答案。
- 第一版默认 `REWARD_PROFILE=orm_v1`，也就是答案正确性为主；等 PRM checkpoint 真有了再切 `prm_v1`。
- 单 48G 第一版默认用 `TRAIN_BATCH_SIZE=16`，每题 `ROLLOUT_N=4`，先求稳定。
- `KL_COEF=0.002` 是轻中等约束，用来防止模型偏离 SFT 太快。
- 如果 OOM，优先把 `MAX_RESPONSE_LENGTH=384` 降到 `256`，再把 `ROLLOUT_N=4` 降到 `2`。

## 9. 当前重要路径

```text
SFT 配置:
configs/llamafactory/qwen25_7b_sft_lora.yaml

12866 clean 数据:
data/sft/v3_12866_train_prop_topup2866/medical_cot_sft_train.clean_13k_public.jsonl

1 epoch LoRA:
saves/qwen25-7b/lora/sft-v3_12866-train-prop-topup2866

2 epoch LoRA:
saves/qwen25-7b/lora/sft-v3_12866-train-prop-topup2866-ep2

MedQA + MedMCQA 测评脚本:
scripts/eval/eval_sft_openai.sh

GRPO 难度采样脚本:
scripts/data/build_grpo_difficulty_data.py

GRPO v1 数据目录:
data/rl/v1_grpo_10k

GRPO 训练脚本:
scripts/train/run_grpo.sh

GRPO reward:
reward/total_reward.py
```
