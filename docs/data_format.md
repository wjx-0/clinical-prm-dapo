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

PRM 数据放在 `data/prm/` 下，可以先采用 pairwise 格式。

```json
{
  "id": "prm_pair_000001",
  "question_id": "medqa_train_000001",
  "chosen": "<think>较好的推理过程</think><answer>C</answer>",
  "rejected": "<think>较差的推理过程</think><answer>B</answer>"
}
```
