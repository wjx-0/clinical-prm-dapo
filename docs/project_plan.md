# 项目计划

## 阶段一：跑通最小闭环

目标是先完成一条最短可复现链路：

```text
MedQA -> 数据清洗 -> SFT -> GRPO/DAPO -> 统一评测
```

## 阶段二：补全 PRM

构造 PRM 训练数据，训练过程 reward model，并接入 GRPO/DAPO 的 reward 函数。

## 阶段三：系统消融

围绕 reward 组件、训练配置、采样策略和模型初始化方式做消融实验。

## 阶段四：案例分析

整理典型正确案例、错误案例和不同训练阶段的行为变化，为论文或报告提供证据。

## 当前优先级

1. 整理 MedQA 原始数据。
2. 生成 `data/processed/medqa_train.jsonl`。
3. 生成 `data/sft/medqa_cot_sft_train.jsonl`。
4. 配置 LLaMA-Factory SFT。
5. 生成 `data/rl/medqa_rl_prompts_train.jsonl`。
6. 配置 verl GRPO/DAPO。
7. 实现基础评测脚本。
