# Reward 设计

本文档记录医学推理后训练中的 reward 设计。

## 设计目标

reward 不只鼓励最终答案正确，还要鼓励模型输出可解析、推理合理、长度受控的医学选择题回答。

## Reward 组件

### 答案 reward

根据 `<answer>` 中抽取出的选项是否等于标准答案打分。

### 格式 reward

检查回复是否包含完整的 `<think>...</think>` 和 `<answer>...</answer>` 结构。

### PRM reward

调用过程 reward model 对推理步骤打分，用于鼓励更可靠的中间推理。

### 一致性 reward

检查推理过程和最终答案是否互相支持，减少“推理选 A，最后答 C”的情况。

### 长度 reward

限制回复过短或过长，避免无效输出和过度推理。

## 第一版总分公式

```text
total_reward = 0.7 * answer_reward
             + 0.2 * format_reward
             + 0.1 * length_reward
```

## 后续版本

接入 PRM 后可以调整为：

```text
total_reward = 0.5 * answer_reward
             + 0.2 * prm_reward
             + 0.15 * format_reward
             + 0.1 * consistency_reward
             + 0.05 * length_reward
```

具体权重需要通过消融实验确定。
