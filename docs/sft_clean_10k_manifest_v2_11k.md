# SFT Clean 10k Manifest v2_11k

## Version

- version: `v2_11k_clean_10k`
- final public file: `data/sft/v2_11k/medical_cot_sft_train.clean_10k_public.jsonl`
- sha256: `fe04765b9efd1bc94a70375175642867ec8fdf42053e5eef9a023283f083428a`
- rows: 10000
- sample seed: `20260606`
- git commit: `1aa1c8bb70fb771cdc4e74f7c08290b0502cb6bb`
- git branch: `main`

## Distribution

### Quality Tier

- `A`: 7025
- `B`: 2975

### Source

- `medmcqa`: 6169
- `medqa`: 3831

### Source / Tier

- `medqa/A`: 3831
- `medmcqa/A`: 3194
- `medmcqa/B`: 2975

### Answer

- `A`: 2654
- `B`: 2584
- `C`: 2468
- `D`: 2294

### Step Count

- `5`: 6601
- `3`: 2975
- `6`: 394
- `4`: 30

## Hard Audit

- `missing_think`: 0
- `missing_answer_tag`: 0
- `answer_mismatch`: 0
- `bad_a_step_count`: 0
- `bad_b_step_count`: 0
- `source_noise`: 0
- `visual_dependency`: 0
- `internal_trace_in_output`: 0
- `public_has_clinical_score`: 0
- `public_has_cot_source`: 0
- `public_has_expected_step_range`: 0
- `public_has_quality_tier`: 0
- `public_has_question_type`: 0

## Files

- `merged_raw_train`: `data/sft/v2_11k/teacher_generated_sft_train.raw.jsonl` (11000 lines, sha256 `7bedff3914ae123453a7bd7e38e8f94f509484a133e6933f75e8a997d6882146`)
- `filtered_clean_train`: `data/sft/v2_11k/medical_cot_sft_train.clean.jsonl` (10679 lines, sha256 `d503a4fb1b52daec6fdca20c5510ab6a78083f0adaa73220e1db9197881b082c`)
- `final_internal_train`: `data/sft/v2_11k/medical_cot_sft_train.clean_10k.jsonl` (10000 lines, sha256 `0be7c813c7445d3cd0e3917c954d5a91f3e0b708544b86e4308582dbed51d77a`)
- `final_public_train`: `data/sft/v2_11k/medical_cot_sft_train.clean_10k_public.jsonl` (10000 lines, sha256 `fe04765b9efd1bc94a70375175642867ec8fdf42053e5eef9a023283f083428a`)
- `quality_rejected`: `data/sft/v2_11k/teacher_generated_sft_rejected_quality.jsonl` (321 lines, sha256 `a1bd8772c4e262d2307852a7a49ac80b0ef0b1fe3dd11a99cc1c6873238e08b7`)
- `review_ready_public`: `data/sft/v2_11k/medical_cot_sft_train.review_ready_public.jsonl` (10384 lines, sha256 `4e7a8b75822a828e1a951b0f76d0c7b56d7bb5ca2ee4e5ad67fb0daab1679e42`)
- manifest json: `data/sft/v2_11k/medical_cot_sft_train.clean_10k_public.manifest.json`
- sha256 file: `data/sft/v2_11k/medical_cot_sft_train.clean_10k_public.sha256`
