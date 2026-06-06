# Teacher SFT 质量过滤报告

## 样本数

- raw train 样本数：100
- raw dev 样本数：0
- final train 样本数：100
- final dev 样本数：0
- final train A 档数量：74
- final train A 档占比：74.00%
- rejected 样本数：0
- overall keep rate：100.00%
- train keep rate：100.00%
- dev keep rate：0.00%

## Reject Reason 分布

- 无

## Source 分布

- `medmcqa`：73
- `medqa`：27

## Quality Tier 分布

- `A`：74
- `B`：26

## Question Type 分布

- `clinical_vignette`：74
- `short_fact`：26

## Quality Tier / Source 分布

- `A/medmcqa`：47
- `A/medqa`：27
- `B/medmcqa`：26

## Answer 分布

- `B`：27
- `A`：25
- `C`：25
- `D`：23

## Subject Top 20

- `<EMPTY>`：27
- `Medicine`：25
- `Gynaecology & Obstetrics`：8
- `Pathology`：8
- `Microbiology`：7
- `Anatomy`：6
- `Surgery`：5
- `Pharmacology`：3
- `Unknown`：3
- `Psychiatry`：2
- `Physiology`：2
- `Radiology`：1
- `Anaesthesia`：1
- `Orthopaedics`：1
- `Pediatrics`：1

## Output 与 Step 统计

- 平均 output 长度：862.76
- 最短 output 长度：406
- 最长 output 长度：1236
- 平均 Step 数：4.50

## Step 数 / Quality Tier

- `A`：5步=72, 6步=2
- `B`：3步=26

## Dirty Input

- dirty_input 数量：0

## Preview

- preview_100 路径：`data/sft/v2_probe/medical_cot_sft_preview_100.jsonl`

## Target Gap

- target_train_size：100
- final train 还差：0

## 最终建议

- PASS：可进入 SFT：格式稳定、保留率较高，未发现答案不一致。
