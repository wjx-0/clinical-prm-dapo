# Teacher SFT Raw 生成报告

- backend：`local`
- model_name：`gpt-5.5`
- num_workers：10
- train 输入数量：100
- dev 输入数量：0
- train raw 生成数量：100
- dev raw 生成数量：0
- rejected_generation 数量：0
- preview_50 路径：`data/sft/v2_probe/teacher_generated_sft_preview_50.jsonl`
- 是否完成全部输入样本：是

## 本次运行统计

- train 新生成：100
- train resume 跳过：0
- train rejected：0
- dev 新生成：0
- dev resume 跳过：0
- dev rejected：0

## rejected reason 分布

- 无

## source 分布

- `medmcqa`：73
- `medqa`：27

## quality_tier 分布

- `A`：74
- `B`：26

## question_type 分布

- `clinical_vignette`：74
- `short_fact`：26

## answer 分布

- `B`：27
- `A`：25
- `C`：25
- `D`：23

## output 长度

- 平均 output 长度：862.76
- 最短 output：406
- 最长 output：1236
