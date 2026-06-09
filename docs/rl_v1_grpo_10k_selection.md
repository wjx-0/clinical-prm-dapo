# GRPO v1 10k Selection

- difficulty_input: `data/rl/v1_grpo_10k/difficulty_samples_epoch1_n4.jsonl`
- output_dir: `data/rl/v1_grpo_10k`
- eligible_rows: 20000
- train_size: 10000
- val_size: 500
- seed: 20260608

## Eligible Difficulty Buckets

- `0`: 3405
- `1`: 2896
- `2`: 2804
- `3`: 3330
- `4`: 7565

## Selected Counts

| split | metric | count |
| --- | --- | --- |
| train | total | 10000 |
| train | source:medmcqa | 6000 |
| train | source:medqa | 4000 |
| train | correct_count:0 | 866 |
| train | correct_count:1 | 2401 |
| train | correct_count:2 | 2602 |
| train | correct_count:3 | 2723 |
| train | correct_count:4 | 1408 |
| train | length:medmcqa/long | 3000 |
| train | length:medmcqa/short | 3000 |
| train | length:medqa/long | 3965 |
| train | length:medqa/short | 35 |
| val | total | 500 |
| val | source:medmcqa | 300 |
| val | source:medqa | 200 |
| val | correct_count:0 | 24 |
| val | correct_count:1 | 126 |
| val | correct_count:2 | 202 |
| val | correct_count:3 | 124 |
| val | correct_count:4 | 24 |
| val | length:medmcqa/long | 150 |
| val | length:medmcqa/short | 150 |
| val | length:medqa/long | 198 |
| val | length:medqa/short | 2 |

## Selected MedMCQA Subject Top 30

- `Medicine`: 776
- `Surgery`: 740
- `Pathology`: 513
- `Anatomy`: 489
- `Gynaecology & Obstetrics`: 435
- `Pediatrics`: 380
- `Microbiology`: 371
- `Pharmacology`: 334
- `Social & Preventive Medicine`: 299
- `Dental`: 274
- `Physiology`: 220
- `Unknown`: 201
- `Ophthalmology`: 191
- `Forensic Medicine`: 166
- `Psychiatry`: 165
- `Biochemistry`: 157
- `ENT`: 151
- `Radiology`: 140
- `Anaesthesia`: 131
- `Orthopaedics`: 109
- `Skin`: 58

## Output Files

- `data/rl/v1_grpo_10k/train.jsonl`
- `data/rl/v1_grpo_10k/train.parquet`
- `data/rl/v1_grpo_10k/val.jsonl`
- `data/rl/v1_grpo_10k/val.parquet`
- `data/rl/v1_grpo_10k/selected_debug.jsonl`
