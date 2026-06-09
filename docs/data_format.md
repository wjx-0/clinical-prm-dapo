# 数据格式

本文档记录项目中各阶段数据的 JSONL 格式约定。

## 原始数据

原始数据放在 `data/raw/` 下，尽量保留数据集原始结构，不直接用于训练。

## 标准 QA 数据

标准化后的选择题数据放在 `data/processed/` 下。

```json
{
  "id": "medqa_train_000001",
  "source": "medqa",
  "split": "train",
  "question": "题干文本",
  "options": {
    "A": "选项 A",
    "B": "选项 B",
    "C": "选项 C",
    "D": "选项 D"
  },
  "answer": "C",
  "explanation": "可选解析"
}
```

## SFT 数据

SFT 数据放在 `data/sft/` 下，第一版建议使用 LLaMA-Factory 支持的 Alpaca 格式。

```json
{
  "instruction": "请解答下面的医学选择题，并给出简洁推理过程，最后用 <answer> 选项 </answer> 输出答案。",
  "input": "题目：...\nA. ...\nB. ...\nC. ...\nD. ...",
  "output": "<think>\n推理过程...\n</think>\n<answer>C</answer>"
}
```

## RL Prompt 数据

RL 数据放在 `data/rl/` 下，用于 verl 的 GRPO/DAPO 阶段。此阶段只提供 prompt 和标准答案，让模型自行生成回复，再由 reward 函数打分。

```json
{
  "data_source": "medqa",
  "prompt": [
    {
      "role": "user",
      "content": "请解答下面的医学选择题...\n题目：...\nA. ...\nB. ...\nC. ...\nD. ..."
    }
  ],
  "reward_model": {
    "style": "rule",
    "ground_truth": "C"
  },
  "extra_info": {
    "id": "medqa_train_000001",
    "split": "train"
  }
}
```

## PRM 数据

PRM 数据放在 `data/prm/` 下，第一版采用 LLaMA-Factory reward-model
训练可读的 pairwise/ranking Alpaca 格式。`chosen` 来自审核后的 clean
SFT reasoning，`rejected` 来自同题真实 rejected 样本或基于原 reasoning
构造的过程扰动负样本，并用 `negative_type` 记录负样本来源。

```json
{
  "id": "medqa_train_000001_prm_pair_01_truncated_reasoning",
  "question_id": "medqa_train_000001",
  "instruction": "Please solve the following medical multiple-choice question...",
  "input": "Question:\n...\n\nOptions:\nA. ...\nB. ...\nC. ...\nD. ...",
  "chosen": "<think>\nStep 1: ...\n</think>\n<answer>C</answer>",
  "rejected": "<think>\nStep 1: ...\n</think>\n<answer>C</answer>",
  "answer": "C",
  "answer_text": "选项 C 文本",
  "negative_type": "truncated_reasoning"
}
```

默认构造命令：

```bash
python scripts/data/build_prm_data.py
```

默认输出：

```text
data/prm/v1_12866_process_rm/prm_pairwise_train.jsonl
data/prm/v1_12866_process_rm/prm_pairwise_val.jsonl
data/prm/v1_12866_process_rm/dataset_info.json
docs/data_stats_prm_v1_12866.md
```
