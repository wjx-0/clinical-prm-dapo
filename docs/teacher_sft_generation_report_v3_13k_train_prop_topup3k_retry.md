# Teacher SFT Raw 生成报告

- backend：`local`
- model_name：`gpt-5.5`
- num_workers：10
- train 输入数量：3000
- dev 输入数量：0
- train raw 生成数量：2951
- dev raw 生成数量：0
- rejected_generation 数量：437
- preview_50 路径：`data/sft/v3_13k_train_prop_topup3k_retry/teacher_generated_sft_preview_50.jsonl`
- 是否完成全部输入样本：是

## 本次运行统计

- train 新生成：339
- train resume 跳过：2612
- train rejected：49
- dev 新生成：0
- dev resume 跳过：0
- dev rejected：0

## rejected reason 分布

- `api_error`：437

## source 分布

- `medmcqa`：2951

## quality_tier 分布

- `B`：2882
- `A`：69

## question_type 分布

- `short_fact`：2882
- `clinical_vignette`：69

## answer 分布

- `A`：849
- `B`：796
- `C`：699
- `D`：607

## output 长度

- 平均 output 长度：484.53
- 最短 output：261
- 最长 output：1178
