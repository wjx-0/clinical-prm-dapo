# Teacher SFT Raw 生成报告

- backend：`local`
- model_name：`gpt-5.5`
- num_workers：10
- train 输入数量：5000
- dev 输入数量：0
- train raw 生成数量：4450
- dev raw 生成数量：0
- rejected_generation 数量：601
- preview_50 路径：`data/sft/teacher_generated_sft_preview_50.jsonl`
- 是否完成全部输入样本：是

## 本次运行统计

- train 新生成：3998
- train resume 跳过：452
- train rejected：550
- dev 新生成：0
- dev resume 跳过：0
- dev rejected：0

## rejected reason 分布

- `api_error`：601

## source 分布

- `medmcqa`：3330
- `medqa`：1120

## answer 分布

- `A`：1263
- `B`：1165
- `C`：1073
- `D`：949

## output 长度

- 平均 output 长度：838.97
- 最短 output：457
- 最长 output：1287
