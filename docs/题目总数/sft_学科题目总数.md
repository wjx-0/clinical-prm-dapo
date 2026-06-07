# SFT 学科题目总数

- generated_at_utc: `2026-06-07T06:03:08+00:00`
- internal_file: `data/sft/v2_11k/medical_cot_sft_train.clean_10k.jsonl`
- public_file: `data/sft/v2_11k/medical_cot_sft_train.clean_10k_public.jsonl`
- internal_rows: 10000
- public_rows: 10000
- note: 本报告以 internal clean_10k 文件为准，因为它保留 `quality_tier/question_type/clinical_score` 等内部元数据；public 文件去掉了这些训练元数据，但题目和学科分布一致。

## Source 总数

| source | 题数 | 占比 |
| --- | ---: | --- |
| medmcqa | 6169 | 61.69% |
| medqa | 3831 | 38.31% |

## Quality Tier 总数

| quality_tier | 题数 | 占比 |
| --- | ---: | --- |
| A | 7025 | 70.25% |
| B | 2975 | 29.75% |

## Question Type 总数

| question_type | 题数 | 占比 |
| --- | ---: | --- |
| clinical_vignette | 7025 | 70.25% |
| short_fact | 2975 | 29.75% |

## Source / Question Type

| source | question_type | 题数 | 占比 |
| --- | --- | ---: | --- |
| medqa | clinical_vignette | 3831 | 38.31% |
| medmcqa | clinical_vignette | 3194 | 31.94% |
| medmcqa | short_fact | 2975 | 29.75% |

## 各学科总数

| subject | total | total_pct | medmcqa | medqa |
| --- | ---: | ---: | --- | --- |
| <EMPTY> | 3831 | 38.31% | 0 | 3831 |
| Medicine | 1192 | 11.92% | 1192 | 0 |
| Pathology | 990 | 9.90% | 990 | 0 |
| Surgery | 730 | 7.30% | 730 | 0 |
| Gynaecology & Obstetrics | 416 | 4.16% | 416 | 0 |
| Pediatrics | 413 | 4.13% | 413 | 0 |
| Anatomy | 410 | 4.10% | 410 | 0 |
| Microbiology | 318 | 3.18% | 318 | 0 |
| Pharmacology | 267 | 2.67% | 267 | 0 |
| Unknown | 215 | 2.15% | 215 | 0 |
| Psychiatry | 204 | 2.04% | 204 | 0 |
| Dental | 159 | 1.59% | 159 | 0 |
| ENT | 129 | 1.29% | 129 | 0 |
| Radiology | 118 | 1.18% | 118 | 0 |
| Biochemistry | 108 | 1.08% | 108 | 0 |
| Orthopaedics | 104 | 1.04% | 104 | 0 |
| Ophthalmology | 102 | 1.02% | 102 | 0 |
| Anaesthesia | 87 | 0.87% | 87 | 0 |
| Skin | 78 | 0.78% | 78 | 0 |
| Physiology | 56 | 0.56% | 56 | 0 |
| Social & Preventive Medicine | 38 | 0.38% | 38 | 0 |
| Forensic Medicine | 35 | 0.35% | 35 | 0 |

## 元数据说明

- `<EMPTY>` 主要来自 MedQA；当前 MedQA 标准化数据没有学科标签。
- `Unknown` 是 MedMCQA 原始/标准化数据中的显式学科值，不等同于空字段。
