# MedQA 学科题目总数

- generated_at_utc: `2026-06-07T06:03:06+00:00`
- note: 统计 processed MedQA 的 train/dev/test；该数据当前没有学科标签。

## Split 总数

| split | path | 题数 | 占比 |
| --- | --- | ---: | --- |
| train | `data/processed/medqa_train.jsonl` | 10178 | 80.00% |
| dev | `data/processed/medqa_dev.jsonl` | 1272 | 10.00% |
| test | `data/processed/medqa_test.jsonl` | 1273 | 10.01% |

## 各学科总数

| subject | total | train | dev | test | total_pct |
| --- | ---: | ---: | ---: | ---: | ---: |
| <EMPTY> | 12723 | 10178 | 1272 | 1273 | 100.00% |

## 元数据说明

- `<EMPTY>` 表示该样本的 `subject` 字段为空。
- 当前标准化后的 MedQA 数据没有可用学科标签，因此 MedQA 会全部落在 `<EMPTY>`。

## Topic Top 30

| topic | 题数 | 占比 |
| --- | ---: | --- |
| <EMPTY> | 12723 | 100.00% |
