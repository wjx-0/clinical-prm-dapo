# Teacher SFT 质量过滤报告

## 样本数

- raw train 样本数：2951
- raw dev 样本数：0
- final train 样本数：2867
- final dev 样本数：0
- final train A 档数量：68
- final train A 档占比：2.37%
- rejected 样本数：84
- overall keep rate：97.15%
- train keep rate：97.15%
- dev keep rate：0.00%

## Reject Reason 分布

- `dirty_input`：40
- `step_3_too_short`：32
- `truncated_last_step`：4
- `answer_text_not_supported`：3
- `step_2_too_short`：2
- `explicit_wrong_answer_mention`：1
- `too_many_steps_for_tier_B`：1
- `step_5_too_short`：1

## Source 分布

- `medmcqa`：2867

## Quality Tier 分布

- `B`：2799
- `A`：68

## Question Type 分布

- `short_fact`：2799
- `clinical_vignette`：68

## Quality Tier / Source 分布

- `B/medmcqa`：2799
- `A/medmcqa`：68

## Answer 分布

- `A`：831
- `B`：770
- `C`：678
- `D`：588

## Subject Top 20

- `Social & Preventive Medicine`：433
- `Pharmacology`：336
- `Physiology`：307
- `Anatomy`：254
- `Biochemistry`：245
- `Dental`：231
- `Forensic Medicine`：207
- `Microbiology`：201
- `Ophthalmology`：196
- `ENT`：95
- `Surgery`：92
- `Radiology`：83
- `Gynaecology & Obstetrics`：70
- `Anaesthesia`：58
- `Orthopaedics`：35
- `Psychiatry`：15
- `Skin`：9

## Output 与 Step 统计

- 平均 output 长度：485.36
- 最短 output 长度：261
- 最长 output 长度：1178
- 平均 Step 数：3.05

## Step 数 / Quality Tier

- `A`：5步=65, 6步=3
- `B`：3步=2799

## Dirty Input

- dirty_input 数量：40

## Preview

- preview_100 路径：`data/sft/v3_13k_train_prop_topup3k_retry/medical_cot_sft_preview_100.jsonl`

## Target Gap

- target_train_size：2951
- final train 还差：84

## 最终建议

- WARNING：可训练但建议人工抽查：final train 数量未达到目标。
