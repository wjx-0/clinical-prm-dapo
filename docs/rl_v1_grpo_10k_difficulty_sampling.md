# GRPO v1 Difficulty Sampling

- candidate_input: `data/rl/v1_grpo_10k/difficulty_candidate_pool.jsonl`
- output: `data/rl/v1_grpo_10k/difficulty_samples_epoch1_n4.jsonl`
- model: `qwen25_7b_sft_v3_12866`
- num_generations: 4
- temperature: 0.7
- top_p: 0.95
- max_tokens: 768
- total_rows: 20000
- error_rows: 0

## Source Counts

- `medmcqa`: 15000
- `medqa`: 5000

## Difficulty Bucket Counts

- `easy_4_of_4`: 7565
- `hard_0_of_4`: 3405
- `medium_2_of_4`: 2804
- `medium_easy_3_of_4`: 3330
- `medium_hard_1_of_4`: 2896

## Source x Difficulty Bucket

- `medmcqa/easy_4_of_4`: 5853
- `medmcqa/hard_0_of_4`: 2623
- `medmcqa/medium_2_of_4`: 1961
- `medmcqa/medium_easy_3_of_4`: 2396
- `medmcqa/medium_hard_1_of_4`: 2167
- `medqa/easy_4_of_4`: 1712
- `medqa/hard_0_of_4`: 782
- `medqa/medium_2_of_4`: 843
- `medqa/medium_easy_3_of_4`: 934
- `medqa/medium_hard_1_of_4`: 729

## Returned Generation Counts

- `4`: 20000
