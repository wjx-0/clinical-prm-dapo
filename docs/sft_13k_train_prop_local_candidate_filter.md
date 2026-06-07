# SFT 13k Local Candidate Filter

- generated_at_utc: `2026-06-07T06:56:01+00:00`
- base_sft: `data/sft/v2_11k/medical_cot_sft_train.clean_10k.jsonl`
- processed_medmcqa_train: `data/processed/medmcqa_train.jsonl`
- output: `data/sft/v3_13k_train_prop_local_candidates/local_reusable_clean.jsonl`
- rejected_output: `data/sft/v3_13k_train_prop_local_candidates/local_reusable_rejected.jsonl`
- kept_rows: 638
- rejected_rows: 30159

## Candidate File Counts

- `data/sft/v2_11k/medical_cot_sft_train.review_ready_pass.jsonl`: total=10384, kept=560
- `data/sft/v2_11k/medical_cot_sft_train.clean.jsonl`: total=10679, kept=76
- `data/sft/v2_eval1000/medical_cot_sft_train.review_ready_pass.jsonl`: total=925, kept=0
- `data/sft/v2_eval1000/medical_cot_sft_train.clean.jsonl`: total=984, kept=0
- `data/sft/v2_eval300/medical_cot_sft_train.review_ready_pass.jsonl`: total=242, kept=1
- `data/sft/v2_eval300/medical_cot_sft_train.clean.jsonl`: total=297, kept=0
- `data/sft/v2_probe/medical_cot_sft_train.clean.jsonl`: total=100, kept=0
- `data/sft/medical_cot_sft_train.clean.jsonl`: total=3086, kept=1
- `data/sft/medical_cot_sft_train.clean_plus_short_fact.jsonl`: total=4100, kept=0

## Kept Quality Tier

- `B`: 618
- `A`: 20

## Kept Question Type

- `short_fact`: 618
- `clinical_vignette`: 20

## Kept Step Count

- `3`: 618
- `5`: 19
- `6`: 1

## Kept Subject Top 30

- `Medicine`: 97
- `Surgery`: 86
- `Pediatrics`: 54
- `Gynaecology & Obstetrics`: 51
- `Anatomy`: 51
- `Pathology`: 50
- `Pharmacology`: 38
- `Microbiology`: 30
- `Psychiatry`: 24
- `Ophthalmology`: 22
- `Dental`: 20
- `Unknown`: 20
- `ENT`: 17
- `Radiology`: 16
- `Skin`: 16
- `Orthopaedics`: 12
- `Biochemistry`: 10
- `Anaesthesia`: 8
- `Forensic Medicine`: 7
- `Social & Preventive Medicine`: 6
- `Physiology`: 3

## Reject Reasons Top 30

- `already_in_base_10k`: 23300
- `not_medmcqa`: 10381
- `too_many_steps_for_tier_B`: 3638
- `teacher_input_tier_c_ambiguous_true_except`: 714
- `duplicate_candidate_id`: 690
- `teacher_input_tier_c_source_noise`: 331
- `teacher_input_tier_c_too_short_for_teacher`: 247
- `dirty_input`: 57
- `teacher_input_tier_c_exam_artifact`: 38
- `teacher_input_tier_c_composite_answer`: 24
- `teacher_input_tier_c_image_dependent`: 21
- `hard_audit_visual_dependency`: 5

## Hard Audit

- `duplicate_ids`: 0
