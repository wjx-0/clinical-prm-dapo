# MedQA Train Stride-2 5k GRPO Data

- input: `data/processed/medqa_train.jsonl`
- output_dir: `data/rl/medqa_train_stride2_5k`
- raw_rows: 10178
- valid_rows: 10178
- train_selection: even-index rows from valid `medqa_train`, first 5000
- val_selection: odd-index rows from valid `medqa_train`, first 500
- train_size: 5000
- val_size: 500
- long_threshold_question_chars: 180
- avg_train_prompt_chars: 1247.76
- avg_val_prompt_chars: 1241.97

## Train Answer Counts

- `A`: 1277
- `B`: 1318
- `C`: 1223
- `D`: 1182

## Val Answer Counts

- `A`: 125
- `B`: 117
- `C`: 135
- `D`: 123

## Length Buckets

- `train/long`: 4975
- `train/short`: 25
- `val/long`: 499
- `val/short`: 1

## Output Files

- `data/rl/medqa_train_stride2_5k/train.jsonl`
- `data/rl/medqa_train_stride2_5k/train.parquet`
- `data/rl/medqa_train_stride2_5k/val.jsonl`
- `data/rl/medqa_train_stride2_5k/val.parquet`
- `data/rl/medqa_train_stride2_5k/selected_debug.jsonl`
