# Teacher Input Topup v3_13k_train_prop_topup3k

- generated_at_utc: `2026-06-07T06:41:54+00:00`
- seed: `20260607`
- target_size: 3000
- target_a_ratio: 0.52
- output_train: `data/teacher_inputs/v3_13k_train_prop_topup3k/teacher_sft_train_inputs.jsonl`
- output_dev: `data/teacher_inputs/v3_13k_train_prop_topup3k/teacher_sft_dev_inputs.jsonl`
- base_sft: `data/sft/v2_11k/medical_cot_sft_train.clean_10k.jsonl`
- processed_medmcqa_train: `data/processed/medmcqa_train.jsonl`
- excluded_ids: 11000
- excluded_questions: 11000

## Selected Distribution

### Quality Tier

- `B`: 2927
- `A`: 73

### Question Type

- `short_fact`: 2927
- `clinical_vignette`: 73

### Answer

- `A`: 864
- `B`: 808
- `C`: 714
- `D`: 614

## Subject Quotas

| subject | sft_now | medmcqa_train_pct | target_after_topup | raw_deficit | quota | candidate_count | selected |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Social & Preventive Medicine | 38 | 6.50% | 596 | 558 | 464 | 7002 | 464 |
| Pharmacology | 267 | 7.53% | 690 | 423 | 352 | 7710 | 352 |
| Physiology | 56 | 4.83% | 443 | 387 | 322 | 5257 | 322 |
| Anatomy | 410 | 7.96% | 730 | 320 | 266 | 7659 | 266 |
| Biochemistry | 108 | 4.53% | 415 | 307 | 255 | 5151 | 255 |
| Dental | 159 | 4.89% | 448 | 289 | 240 | 6470 | 240 |
| Forensic Medicine | 35 | 3.23% | 296 | 261 | 217 | 3424 | 217 |
| Microbiology | 318 | 6.19% | 567 | 249 | 207 | 6131 | 207 |
| Ophthalmology | 102 | 3.79% | 348 | 246 | 204 | 3846 | 204 |
| ENT | 129 | 2.69% | 247 | 118 | 98 | 2680 | 98 |
| Surgery | 730 | 9.22% | 846 | 116 | 96 | 9696 | 96 |
| Radiology | 118 | 2.40% | 220 | 102 | 85 | 2745 | 85 |
| Gynaecology & Obstetrics | 416 | 5.48% | 502 | 86 | 71 | 5836 | 71 |
| Anaesthesia | 87 | 1.74% | 159 | 72 | 60 | 1855 | 60 |
| Orthopaedics | 104 | 1.64% | 150 | 46 | 38 | 1652 | 38 |
| Psychiatry | 204 | 2.43% | 223 | 19 | 16 | 2422 | 16 |
| Skin | 78 | 0.97% | 89 | 11 | 9 | 955 | 9 |

## Filter Reasons Top 30

- `duplicate_question`: 27585
- `tier_c_ambiguous_true_except`: 22983
- `tier_c_too_short_for_teacher`: 15787
- `duplicate_id`: 7100
- `tier_c_source_noise`: 4258
- `tier_c_composite_answer`: 4190
- `short_question`: 3882
- `tier_c_dirty_text`: 991
- `tier_c_image_dependent`: 952
- `tier_c_exam_artifact`: 930
- `option_duplicate`: 665
- `empty_option_A`: 43
- `empty_option_B`: 43
- `empty_option_C`: 42
- `empty_option_D`: 30
