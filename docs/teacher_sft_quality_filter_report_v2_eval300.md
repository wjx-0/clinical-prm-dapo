# Teacher SFT 质量过滤报告

## 样本数

- raw train 样本数：300
- raw dev 样本数：0
- final train 样本数：297
- final dev 样本数：0
- final train A 档数量：222
- final train A 档占比：74.75%
- rejected 样本数：3
- overall keep rate：99.00%
- train keep rate：99.00%
- dev keep rate：0.00%

## Reject Reason 分布

- `step_5_too_short`：2
- `truncated_last_step`：1

## Source 分布

- `medmcqa`：207
- `medqa`：90

## Quality Tier 分布

- `A`：222
- `B`：75

## Question Type 分布

- `clinical_vignette`：222
- `short_fact`：75

## Quality Tier / Source 分布

- `A/medmcqa`：132
- `A/medqa`：90
- `B/medmcqa`：75

## Answer 分布

- `A`：79
- `C`：75
- `B`：72
- `D`：71

## Subject Top 20

- `<EMPTY>`：90
- `Medicine`：73
- `Pathology`：38
- `Surgery`：17
- `Gynaecology & Obstetrics`：17
- `Microbiology`：10
- `Pharmacology`：9
- `Anatomy`：9
- `Unknown`：9
- `Pediatrics`：7
- `Physiology`：4
- `Radiology`：4
- `Psychiatry`：4
- `Biochemistry`：2
- `Orthopaedics`：2
- `Ophthalmology`：1
- `Anaesthesia`：1

## Output 与 Step 统计

- 平均 output 长度：860.93
- 最短 output 长度：385
- 最长 output 长度：1307
- 平均 Step 数：4.56

## Step 数 / Quality Tier

- `A`：5步=204, 6步=18
- `B`：3步=75

## Dirty Input

- dirty_input 数量：0

## Preview

- preview_100 路径：`data/sft/v2_eval300/medical_cot_sft_preview_100.jsonl`

## Target Gap

- target_train_size：300
- final train 还差：3

## 最终建议

- WARNING：可训练但建议人工抽查：final train 数量未达到目标。
