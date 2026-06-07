# 题目总数统计

- generated_at_utc: `2026-06-07T06:03:08+00:00`

## 文件

- [MedQA 学科题目总数](medqa_学科题目总数.md)
- [MedMCQA 学科题目总数](medmcqa_学科题目总数.md)
- [SFT 学科题目总数](sft_学科题目总数.md)

## 快速结论

- MedQA processed train/dev/test 总数分别为 10178/1272/1273，但 `subject` 字段均为空，无法从现有标准化文件统计真实学科分布。
- MedMCQA processed train/dev/test_unlabeled 总数分别为 182822/4183/6150；`medmcqa_test.jsonl` 为 0 行，因为官方 test 没有标签。
- SFT clean_10k 使用 internal 文件统计，共 10000 条，其中 MedQA 3831 条、MedMCQA 6169 条。
