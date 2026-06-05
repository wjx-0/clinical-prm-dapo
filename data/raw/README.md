# 原始数据下载记录

本文档记录 `data/raw/` 下原始数据的来源、文件和校验信息。

## MedQA-English

来源：`GBaker/MedQA-USMLE-4-options-hf`

下载位置：

- `data/raw/medqa/train.json`
- `data/raw/medqa/dev.json`
- `data/raw/medqa/test.json`

注意：这三个文件扩展名是 `.json`，但实际内容是 JSONL，一行一条样本。

本地检查结果：

- `train.json`：10,178 条
- `dev.json`：1,272 条
- `test.json`：1,273 条

字段：

- `id`
- `sent1`
- `sent2`
- `ending0`
- `ending1`
- `ending2`
- `ending3`
- `label`

## MedMCQA

来源：`openlifescienceai/medmcqa`

下载位置：

- `data/raw/medmcqa/train-00000-of-00001.parquet`
- `data/raw/medmcqa/validation-00000-of-00001.parquet`
- `data/raw/medmcqa/test-00000-of-00001.parquet`

官方 split 数量：

- train：182,822 条
- validation：4,183 条
- test：6,150 条

本地 SHA256：

```text
b119434ba551517a6ec0ba1f7e0b4c029165ed284a4704f262ce37c791c493c5  train-00000-of-00001.parquet
b768a1ea34afc9f80d3106d9b21f80fa8a00ec450a1f6cd641af72ca9e591021  validation-00000-of-00001.parquet
1d308841f0c82df363d3d638b33b69b8abd266b1e615ae5d2607dbb24c70beb1  test-00000-of-00001.parquet
```

