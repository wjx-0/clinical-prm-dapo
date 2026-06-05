# 评测指标

本文档用于记录训练和评测阶段关注的指标。

## 离线评测指标

- Accuracy：最终答案准确率
- Format Pass Rate：回复是否满足 `<think>` 和 `<answer>` 格式
- Answer Extraction Rate：能否成功抽取最终选项
- Average Response Length：平均回复长度
- Error Type Distribution：错误类型分布

## Reward 指标

- Answer Reward Mean：答案 reward 均值
- Format Reward Mean：格式 reward 均值
- PRM Score Mean：过程 reward 均值
- Length Reward Mean：长度 reward 均值
- Total Reward Mean：总 reward 均值

## RL 训练指标

- Valid Group Ratio：有效样本组比例
- KL：policy 与 reference model 的 KL
- Entropy：生成分布熵
- Response Length：RL rollout 回复长度
- Clip Fraction：策略更新裁剪比例

## 对比维度

建议至少比较：

- Base model
- SFT model
- GRPO model
- DAPO model
- 加 PRM reward 前后
- 不同 reward 权重设置
