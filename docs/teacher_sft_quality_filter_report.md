# Teacher SFT 质量过滤报告

## 样本数

- raw train 样本数：4450
- raw dev 样本数：0
- final train 样本数：4395
- final dev 样本数：0
- rejected 样本数：55
- overall keep rate：98.76%
- train keep rate：98.76%
- dev keep rate：0.00%

## Reject Reason 分布

- `truncated_last_step`：20
- `answer_text_not_supported`：17
- `step_5_too_short`：9
- `step_3_too_short`：4
- `explicit_wrong_answer_mention`：2
- `step_4_too_short`：2
- `low_input_keyword_coverage`：1
- `step_6_too_short`：1

## Source 分布

- `medmcqa`：3288
- `medqa`：1107

## Answer 分布

- `A`：1243
- `B`：1155
- `C`：1066
- `D`：931

## Subject Top 20

- `<EMPTY>`：1107
- `Medicine`：341
- `Anatomy`：311
- `Surgery`：301
- `Pathology`：255
- `Pharmacology`：233
- `Microbiology`：209
- `Biochemistry`：198
- `Social & Preventive Medicine`：188
- `Gynaecology & Obstetrics`：179
- `Pediatrics`：171
- `Physiology`：169
- `Ophthalmology`：107
- `ENT`：97
- `Psychiatry`：80
- `Radiology`：80
- `Dental`：79
- `Forensic Medicine`：79
- `Unknown`：59
- `Orthopaedics`：58

## Output 与 Step 统计

- 平均 output 长度：839.37
- 最短 output 长度：457
- 最长 output 长度：1287
- 平均 Step 数：4.43

## Dirty Input

- dirty_input 数量：15

## Preview

- preview_100 路径：`data/sft/medical_cot_sft_preview_100.jsonl`

## Target Gap

- target_train_size：10000
- final train 还差：5605

## 最终建议

- WARNING：可训练但建议人工抽查：final train 数量未达到目标。
