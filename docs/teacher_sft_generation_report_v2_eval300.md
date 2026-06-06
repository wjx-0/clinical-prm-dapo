# Teacher SFT Raw 生成报告

- backend：`local`
- model_name：`gpt-5.5`
- num_workers：10
- train 输入数量：300
- dev 输入数量：0
- train raw 生成数量：300
- dev raw 生成数量：0
- rejected_generation 数量：0
- preview_50 路径：`data/sft/v2_eval300/teacher_generated_sft_preview_50.jsonl`
- 是否完成全部输入样本：是

## 本次运行统计

- train 新生成：300
- train resume 跳过：0
- train rejected：0
- dev 新生成：0
- dev resume 跳过：0
- dev rejected：0

## rejected reason 分布

- 无

## source 分布

- `medmcqa`：210
- `medqa`：90

## quality_tier 分布

- `A`：225
- `B`：75

## question_type 分布

- `clinical_vignette`：225
- `short_fact`：75

## answer 分布

- `A`：79
- `C`：77
- `B`：73
- `D`：71

## output 长度

- 平均 output 长度：860.99
- 最短 output：385
- 最长 output：1307
