# Teacher SFT 质量过滤报告

## 样本数

- raw train 样本数：1000
- raw dev 样本数：0
- final train 样本数：984
- final dev 样本数：0
- final train A 档数量：742
- final train A 档占比：75.41%
- rejected 样本数：16
- overall keep rate：98.40%
- train keep rate：98.40%
- dev keep rate：0.00%

## Reject Reason 分布

- `dirty_input`：10
- `step_5_too_short`：2
- `step_6_too_short`：2
- `step_3_too_short`：1
- `truncated_last_step`：1

## Source 分布

- `medmcqa`：684
- `medqa`：300

## Quality Tier 分布

- `A`：742
- `B`：242

## Question Type 分布

- `clinical_vignette`：742
- `short_fact`：242

## Quality Tier / Source 分布

- `A/medmcqa`：442
- `A/medqa`：300
- `B/medmcqa`：242

## Answer 分布

- `A`：259
- `C`：259
- `D`：235
- `B`：231

## Subject Top 20

- `<EMPTY>`：300
- `Medicine`：226
- `Pathology`：154
- `Surgery`：58
- `Anatomy`：37
- `Gynaecology & Obstetrics`：37
- `Unknown`：31
- `Pediatrics`：26
- `Microbiology`：21
- `Pharmacology`：21
- `Psychiatry`：15
- `Radiology`：12
- `Orthopaedics`：9
- `Biochemistry`：9
- `Anaesthesia`：7
- `Physiology`：7
- `ENT`：6
- `Ophthalmology`：4
- `Dental`：2
- `Skin`：2

## Output 与 Step 统计

- 平均 output 长度：853.70
- 最短 output 长度：354
- 最长 output 长度：1342
- 平均 Step 数：4.57

## Step 数 / Quality Tier

- `A`：4步=5, 5步=673, 6步=64
- `B`：3步=242

## Dirty Input

- dirty_input 数量：10

## Preview

- preview_100 路径：`data/sft/v2_eval1000/medical_cot_sft_preview_100.jsonl`

## Target Gap

- target_train_size：1000
- final train 还差：16

## 最终建议

- WARNING：可训练但建议人工抽查：final train 数量未达到目标。
