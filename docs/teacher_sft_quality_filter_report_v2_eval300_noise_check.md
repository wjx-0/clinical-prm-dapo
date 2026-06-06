# Teacher SFT 质量过滤报告

## 样本数

- raw train 样本数：300
- raw dev 样本数：0
- final train 样本数：264
- final dev 样本数：0
- final train A 档数量：201
- final train A 档占比：76.14%
- rejected 样本数：36
- overall keep rate：88.00%
- train keep rate：88.00%
- dev keep rate：0.00%

## Reject Reason 分布

- `dirty_input`：34
- `step_5_too_short`：2
- `truncated_last_step`：1

## Source 分布

- `medmcqa`：174
- `medqa`：90

## Quality Tier 分布

- `A`：201
- `B`：63

## Question Type 分布

- `clinical_vignette`：201
- `short_fact`：63

## Quality Tier / Source 分布

- `A/medmcqa`：111
- `A/medqa`：90
- `B/medmcqa`：63

## Answer 分布

- `A`：73
- `C`：67
- `B`：64
- `D`：60

## Subject Top 20

- `<EMPTY>`：90
- `Medicine`：67
- `Pathology`：35
- `Gynaecology & Obstetrics`：12
- `Surgery`：12
- `Unknown`：8
- `Anatomy`：8
- `Microbiology`：8
- `Pediatrics`：6
- `Pharmacology`：5
- `Psychiatry`：3
- `Physiology`：3
- `Radiology`：2
- `Biochemistry`：2
- `Orthopaedics`：2
- `Ophthalmology`：1

## Output 与 Step 统计

- 平均 output 长度：870.14
- 最短 output 长度：385
- 最长 output 长度：1307
- 平均 Step 数：4.59

## Step 数 / Quality Tier

- `A`：5步=184, 6步=17
- `B`：3步=63

## Dirty Input

- dirty_input 数量：34

## Preview

- preview_100 路径：`data/sft/v2_eval300_noise_check/medical_cot_sft_preview_100.jsonl`

## Target Gap

- target_train_size：300
- final train 还差：36

## 最终建议

- WARNING：可训练但建议人工抽查：final train 数量未达到目标；dirty_input 较多。
