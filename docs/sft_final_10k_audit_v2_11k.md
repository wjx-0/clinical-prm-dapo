# SFT Final 10k Audit v2_11k

## Summary

- merged raw rows: 11000
- clean rows after quality filter: 10679
- conservative rule PASS rows after residual exclusions: 10384
- final clean_10k rows: 10000
- final public rows: 10000
- removed-from-clean rows: 679
- final selection policy: all A-tier rows with PASS or only `short_final_step` WARN, excluding residual source noise and visual/image-dependent prompts, then B-tier PASS rows to 10,000

## Final 10k Distribution

### Quality Tier

- `A`: 7025
- `B`: 2975

### Source

- `medmcqa`: 6169
- `medqa`: 3831

### Rule Status

- `PASS`: 9824
- `WARN`: 176

### Step Count

- `5`: 6601
- `3`: 2975
- `6`: 394
- `4`: 30

### Warning Types Included

- `short_final_step`: 176

## Hard Audit Checks For Final 10k

- `missing_think`: 0
- `missing_answer_tag`: 0
- `answer_mismatch`: 0
- `bad_a_step_count`: 0
- `bad_b_step_count`: 0
- `source_noise`: 0
- `visual_dependency`: 0
- `internal_trace_in_output`: 0
- `duplicate_ids`: 0

## Public Metadata Audit

- `final_public_has_clinical_score`: 0
- `final_public_has_cot_source`: 0
- `final_public_has_expected_step_range`: 0
- `final_public_has_quality_tier`: 0
- `final_public_has_question_type`: 0
- `review_public_has_clinical_score`: 0
- `review_public_has_cot_source`: 0
- `review_public_has_expected_step_range`: 0
- `review_public_has_quality_tier`: 0
- `review_public_has_question_type`: 0

## Conservative Rule-PASS Pool

- rows: 10384
### Quality Tier

- `A`: 6849
- `B`: 3535

### Source

- `medmcqa`: 6612
- `medqa`: 3772

### Step Count

- `5`: 6449
- `3`: 3535
- `6`: 370
- `4`: 30

## Output Files

- `data/sft/v2_11k/medical_cot_sft_train.clean_10k.jsonl`
- `data/sft/v2_11k/medical_cot_sft_train.clean_10k_public.jsonl`
- `data/sft/v2_11k/medical_cot_sft_train.review_ready_pass.jsonl`
- `data/sft/v2_11k/medical_cot_sft_train.review_ready_public.jsonl`
- `outputs/data_validation/sft_final_selection_removed_v2_11k.jsonl`
