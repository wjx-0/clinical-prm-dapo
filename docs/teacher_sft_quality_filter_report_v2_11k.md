# Teacher SFT 质量过滤报告

## 样本数

- raw train 样本数：11000
- raw dev 样本数：0
- final train 样本数：10679
- final dev 样本数：0
- final train A 档数量：7084
- final train A 档占比：66.34%
- rejected 样本数：321
- overall keep rate：97.08%
- train keep rate：97.08%
- dev keep rate：0.00%

## Reject Reason 分布

- `dirty_input`：190
- `step_5_too_short`：75
- `step_3_too_short`：23
- `step_6_too_short`：15
- `truncated_last_step`：14
- `explicit_wrong_answer_mention`：2
- `too_many_steps_for_tier_B`：2
- `step_2_too_short`：1
- `step_1_too_short`：1

## Source 分布

- `medmcqa`：6810
- `medqa`：3869

## Quality Tier 分布

- `A`：7084
- `B`：3595

## Question Type 分布

- `clinical_vignette`：7084
- `short_fact`：3595

## Quality Tier / Source 分布

- `A/medqa`：3869
- `B/medmcqa`：3595
- `A/medmcqa`：3215

## Answer 分布

- `A`：2831
- `B`：2781
- `C`：2626
- `D`：2441

## Subject Top 20

- `<EMPTY>`：3869
- `Medicine`：1288
- `Pathology`：1040
- `Surgery`：816
- `Gynaecology & Obstetrics`：468
- `Pediatrics`：467
- `Anatomy`：461
- `Microbiology`：348
- `Pharmacology`：305
- `Unknown`：235
- `Psychiatry`：228
- `Dental`：180
- `ENT`：146
- `Radiology`：136
- `Ophthalmology`：124
- `Biochemistry`：118
- `Orthopaedics`：116
- `Anaesthesia`：95
- `Skin`：94
- `Physiology`：59

## Output 与 Step 统计

- 平均 output 长度：782.32
- 最短 output 长度：284
- 最长 output 长度：1433
- 平均 Step 数：4.36

## Step 数 / Quality Tier

- `A`：4步=30, 5步=6660, 6步=394
- `B`：3步=3595

## Dirty Input

- dirty_input 数量：190

## Preview

- preview_100 路径：`data/sft/v2_11k/medical_cot_sft_preview_100.jsonl`

## Target Gap

- target_train_size：10000
- final train 还差：0

## 最终建议

- PASS：可进入 SFT：格式稳定、保留率较高，未发现答案不一致。
