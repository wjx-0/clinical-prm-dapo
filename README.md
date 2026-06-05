# clinical-prm-dapo

Post-training project scaffold for medical reasoning experiments with
LLaMA-Factory and verl.

This repository keeps the project code outside the training frameworks. The
frameworks own the trainer loops; this project owns data preparation, YAML
configs, reward functions, evaluation, and experiment records.

## Workflow

1. Prepare raw QA data into a normalized JSONL format.
2. Build SFT data for LLaMA-Factory.
3. Run baseline evaluation.
4. Run SFT with LLaMA-Factory configs.
5. Build PRM data and train a process reward model.
6. Run GRPO/DAPO with verl configs and project reward functions.
7. Evaluate all checkpoints and compare experiment runs.

## Layout

```text
data/                  raw, processed, SFT, PRM, and RL prompt data
configs/llamafactory/  LLaMA-Factory YAML configs
configs/verl/          verl GRPO/DAPO YAML configs
reward/                answer, format, PRM, length, and total rewards
eval/                  inference, answer extraction, metrics, analysis
scripts/data/          data preparation entrypoints
scripts/train/         CLI training launchers
scripts/eval/          CLI evaluation launchers
outputs/               model outputs and generated predictions
runs/                  reproducible experiment folders
docs/                  project notes, data format, metrics, ablations
```

## First milestone

Run a minimal path first:

```bash
python scripts/data/prepare_medqa.py
python scripts/data/build_sft_data.py
bash scripts/train/run_sft_3b.sh
python scripts/data/build_rl_prompts.py
bash scripts/train/run_grpo.sh
bash scripts/eval/eval_grpo.sh
```

