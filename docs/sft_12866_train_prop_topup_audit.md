# SFT Train-Proportional Topup Audit

- generated_at_utc: `2026-06-07T08:14:43+00:00`
- base_internal_rows: 10000
- topup_rows: 2866
- final_internal_rows: 12866
- final_public_rows: 12866
- output_dir: `data/sft/v3_12866_train_prop_topup2866`

## Candidate Inputs

- `data/sft/v3_13k_train_prop_topup3k_retry/medical_cot_sft_train.clean.jsonl`: 2867

## Final Source Distribution

- `medmcqa`: 9035
- `medqa`: 3831

## Final Quality Tier

- `A`: 7093
- `B`: 5773

## Final Question Type

- `clinical_vignette`: 7093
- `short_fact`: 5773

## Final Step Count

- `5`: 6666
- `3`: 5773
- `6`: 397
- `4`: 30

## Topup Subject Allocation

| subject | topup_selected | quota | raw_deficit | final_medmcqa_count | final_medmcqa_pct | medmcqa_train_pct |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Social & Preventive Medicine | 433 | 448 | 549 | 471 | 5.21% | 6.50% |
| Pharmacology | 336 | 337 | 413 | 603 | 6.67% | 7.53% |
| Physiology | 307 | 310 | 380 | 363 | 4.02% | 4.83% |
| Anatomy | 254 | 253 | 310 | 664 | 7.35% | 7.96% |
| Biochemistry | 245 | 246 | 301 | 353 | 3.91% | 4.53% |
| Dental | 231 | 231 | 283 | 390 | 4.32% | 4.89% |
| Forensic Medicine | 207 | 210 | 257 | 242 | 2.68% | 3.23% |
| Microbiology | 201 | 197 | 241 | 519 | 5.74% | 6.19% |
| Ophthalmology | 196 | 197 | 241 | 298 | 3.30% | 3.79% |
| ENT | 95 | 93 | 114 | 224 | 2.48% | 2.69% |
| Surgery | 92 | 84 | 103 | 822 | 9.10% | 9.22% |
| Radiology | 82 | 81 | 99 | 200 | 2.21% | 2.40% |
| Gynaecology & Obstetrics | 70 | 65 | 79 | 486 | 5.38% | 5.48% |
| Anaesthesia | 58 | 57 | 70 | 145 | 1.60% | 1.74% |
| Orthopaedics | 35 | 36 | 44 | 139 | 1.54% | 1.64% |
| Psychiatry | 15 | 13 | 16 | 219 | 2.42% | 2.43% |
| Skin | 9 | 8 | 10 | 87 | 0.96% | 0.97% |

## Base Hard Audit

- `duplicate_ids`: 0
- `visual_dependency`: 1

## Topup Hard Audit

- `duplicate_ids`: 0

## Final Hard Audit

- `duplicate_ids`: 0
- `visual_dependency`: 1

## Final Public Metadata Audit

- `duplicate_ids`: 0
- `visual_dependency`: 1

## Output Files

- `data/sft/v3_12866_train_prop_topup2866/medical_cot_sft_train.clean_13k.jsonl`
- `data/sft/v3_12866_train_prop_topup2866/medical_cot_sft_train.clean_13k_public.jsonl`
- `data/sft/v3_12866_train_prop_topup2866/medical_cot_sft_train.topup_3k.jsonl`
- `data/sft/v3_12866_train_prop_topup2866/medical_cot_sft_train.topup_3k_public.jsonl`
- `data/sft/v3_12866_train_prop_topup2866/dataset_info.json`
- `data/sft/v3_12866_train_prop_topup2866/medical_cot_sft_train.clean_13k_public.manifest.json`
- `data/sft/v3_12866_train_prop_topup2866/medical_cot_sft_train.clean_13k_public.sha256`
