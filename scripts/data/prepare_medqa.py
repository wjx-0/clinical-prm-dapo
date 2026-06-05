"""Prepare MedQA-English into normalized multiple-choice QA JSONL files.

The script reads ``openlifescienceai/medqa`` with Hugging Face datasets and
exports:

- data/processed/medqa_train.jsonl
- data/processed/medqa_dev.jsonl
- data/processed/medqa_test.jsonl
- docs/data_stats_medqa.md
"""

from __future__ import annotations

import argparse
import ast
import json
import random
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


DATASET_NAME = "openlifescienceai/medqa"
LETTERS = ("A", "B", "C", "D")
LETTER_BY_INDEX = {0: "A", 1: "B", 2: "C", 3: "D"}
CANONICAL_SPLITS = ("train", "dev", "test")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert openlifescienceai/medqa to normalized QA JSONL."
    )
    parser.add_argument(
        "--output_dir",
        type=Path,
        default=Path("data/processed"),
        help="Directory for processed JSONL files.",
    )
    parser.add_argument(
        "--stats_path",
        type=Path,
        default=Path("docs/data_stats_medqa.md"),
        help="Markdown path for dataset statistics.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed used when generated train/dev/test splits are needed.",
    )
    parser.add_argument(
        "--max_samples",
        type=int,
        default=-1,
        help="Debug limit. If positive, process only the first N raw examples.",
    )
    return parser.parse_args()


def load_medqa_dataset() -> Any:
    try:
        from datasets import load_dataset
    except ImportError as exc:
        raise RuntimeError(
            "缺少依赖 datasets。请先运行：pip install datasets"
        ) from exc

    try:
        return load_dataset(DATASET_NAME)
    except Exception as exc:
        raise RuntimeError(
            f"读取 Hugging Face 数据集失败：{DATASET_NAME}。"
            "请检查网络连接、数据集名称和 Hugging Face 访问权限。"
        ) from exc


def normalize_key(key: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(key).lower())


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return re.sub(r"\s+", " ", value).strip()
    return re.sub(r"\s+", " ", str(value)).strip()


def flatten_record(record: dict[str, Any]) -> dict[str, Any]:
    """Merge top-level fields with nested ``data`` fields when present."""
    flattened = dict(record)
    nested = record.get("data")
    if isinstance(nested, dict):
        flattened.update(nested)
    return flattened


def get_field(record: dict[str, Any], candidates: list[str]) -> Any:
    normalized = {normalize_key(key): value for key, value in record.items()}
    for candidate in candidates:
        key = normalize_key(candidate)
        if key in normalized:
            return normalized[key]
    return None


def canonical_split_name(split_name: str) -> str | None:
    name = split_name.lower()
    if name in {"train", "training"}:
        return "train"
    if name in {"dev", "valid", "validation", "eval", "evaluation"}:
        return "dev"
    if name in {"test", "testing"}:
        return "test"
    return None


def dataset_items(dataset: Any) -> list[tuple[str, dict[str, Any]]]:
    if hasattr(dataset, "keys"):
        items: list[tuple[str, dict[str, Any]]] = []
        for split_name in dataset.keys():
            for record in dataset[split_name]:
                items.append((str(split_name), dict(record)))
        return items

    return [("all", dict(record)) for record in dataset]


def has_complete_canonical_splits(split_names: list[str]) -> bool:
    canonical = {canonical_split_name(name) for name in split_names}
    return all(split in canonical for split in CANONICAL_SPLITS)


def split_examples(
    raw_items: list[tuple[str, dict[str, Any]]], seed: int
) -> dict[str, list[dict[str, Any]]]:
    split_names = sorted({split_name for split_name, _ in raw_items})
    if has_complete_canonical_splits(split_names):
        grouped = {split: [] for split in CANONICAL_SPLITS}
        for source_split, record in raw_items:
            split = canonical_split_name(source_split)
            if split in grouped:
                grouped[split].append(record)
        return grouped

    records = [record for _, record in raw_items]
    rng = random.Random(seed)
    rng.shuffle(records)

    total = len(records)
    train_end = int(total * 0.8)
    dev_end = train_end + int(total * 0.1)
    return {
        "train": records[:train_end],
        "dev": records[train_end:dev_end],
        "test": records[dev_end:],
    }


def canonical_option_key(key: Any) -> str | None:
    if isinstance(key, int):
        return LETTER_BY_INDEX.get(key)

    text = str(key).strip()
    normalized = normalize_key(text)

    if text.upper() in LETTERS:
        return text.upper()
    if normalized in {"0", "1", "2", "3"}:
        return LETTER_BY_INDEX[int(normalized)]
    if normalized in {"a", "b", "c", "d"}:
        return normalized.upper()
    if normalized in {"opa", "opta", "optiona", "choicea", "ending0"}:
        return "A"
    if normalized in {"opb", "optb", "optionb", "choiceb", "ending1"}:
        return "B"
    if normalized in {"opc", "optc", "optionc", "choicec", "ending2"}:
        return "C"
    if normalized in {"opd", "optd", "optiond", "choiced", "ending3"}:
        return "D"

    match = re.match(r"^([abcd])(?:[\.\):_-]|$)", text, flags=re.IGNORECASE)
    if match:
        return match.group(1).upper()

    return None


def parse_options_from_mapping(options: dict[Any, Any]) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for raw_key, raw_value in options.items():
        key = canonical_option_key(raw_key)
        value = clean_text(raw_value)
        if key in LETTERS and value:
            parsed[key] = value
    return parsed


def parse_options_from_sequence(
    options: list[Any] | tuple[Any, ...],
) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for index, value in enumerate(options[:4]):
        parsed[LETTERS[index]] = clean_text(value)
    return parsed


def parse_options_from_labeled_text(options: str) -> dict[str, str]:
    parsed: dict[str, str] = {}

    for line in options.splitlines():
        match = re.match(r"^\s*([A-Da-d])\s*[\.\):、-]\s*(.+?)\s*$", line)
        if match:
            parsed[match.group(1).upper()] = clean_text(match.group(2))

    if len(parsed) == 4:
        return parsed

    pattern = re.compile(
        r"(?:^|\s)([A-Da-d])\s*[\.\):、-]\s*",
        flags=re.MULTILINE,
    )
    matches = list(pattern.finditer(options))
    if len(matches) >= 4:
        parsed = {}
        for index, match in enumerate(matches[:4]):
            start = match.end()
            end = matches[index + 1].start() if index + 1 < len(matches) else len(options)
            parsed[match.group(1).upper()] = clean_text(options[start:end])

    return parsed


def parse_options(raw_options: Any) -> dict[str, str]:
    if isinstance(raw_options, dict):
        return parse_options_from_mapping(raw_options)

    if isinstance(raw_options, (list, tuple)):
        return parse_options_from_sequence(raw_options)

    if isinstance(raw_options, str):
        text = raw_options.strip()
        if not text:
            return {}

        if text[0] in "{[":
            try:
                parsed = ast.literal_eval(text)
            except (SyntaxError, ValueError):
                parsed = None
            if isinstance(parsed, dict):
                return parse_options_from_mapping(parsed)
            if isinstance(parsed, (list, tuple)):
                return parse_options_from_sequence(parsed)

        return parse_options_from_labeled_text(text)

    return {}


def option_letter_from_text(value: Any, options: dict[str, str]) -> str | None:
    text = clean_text(value)
    if not text:
        return None

    for letter, option_text in options.items():
        if clean_text(option_text).lower() == text.lower():
            return letter

    return None


def normalize_answer_value(value: Any, options: dict[str, str]) -> str | None:
    if value is None:
        return None

    if isinstance(value, int):
        return LETTER_BY_INDEX.get(value)

    text = clean_text(value)
    upper = text.upper()
    normalized = normalize_key(text)

    if upper in LETTERS:
        return upper

    match = re.match(r"^([A-D])(?:[\.\):_-]|\s|$)", upper)
    if match:
        return match.group(1)

    if normalized in {"0", "1", "2", "3"}:
        return LETTER_BY_INDEX[int(normalized)]

    letter = option_letter_from_text(text, options)
    if letter:
        return letter

    return None


def extract_answer(record: dict[str, Any], options: dict[str, str]) -> str | None:
    answer_text = get_field(
        record,
        [
            "Correct Answer",
            "correct_answer",
            "answer_text",
            "Answer Text",
            "answer",
        ],
    )
    correct_option = get_field(
        record,
        [
            "Correct Option",
            "correct_option",
            "answer_idx",
            "answer_index",
            "label",
            "cop",
        ],
    )

    answer = normalize_answer_value(correct_option, options)
    if answer in LETTERS:
        return answer

    answer = normalize_answer_value(answer_text, options)
    if answer in LETTERS:
        return answer

    return option_letter_from_text(answer_text, options)


def validate_sample(sample: dict[str, Any]) -> str | None:
    if not sample["question"]:
        return "question_empty"

    options = sample["options"]
    if any(letter not in options for letter in LETTERS):
        return "missing_options"
    if any(not clean_text(options.get(letter)) for letter in LETTERS):
        return "option_empty"
    if sample["answer"] not in LETTERS:
        return "invalid_answer"
    if not sample["answer_text"]:
        return "answer_text_empty"

    return None


def convert_record(
    record: dict[str, Any],
    split: str,
    index: int,
) -> tuple[dict[str, Any] | None, str | None]:
    payload = flatten_record(record)

    question = clean_text(
        get_field(payload, ["Question", "question", "stem", "prompt", "problem"])
    )
    raw_options = get_field(payload, ["Options", "options", "choices", "Choices"])
    options = parse_options(raw_options)

    answer = extract_answer(payload, options)
    answer_text = options.get(answer, "") if answer else ""

    sample = {
        "id": f"medqa_{split}_{index:06d}",
        "source": "medqa",
        "split": split,
        "language": "en",
        "question": question,
        "options": {letter: options.get(letter, "") for letter in LETTERS},
        "answer": answer or "",
        "answer_text": answer_text,
        "explanation": clean_text(
            get_field(payload, ["Explanation", "explanation", "rationale", "reason"])
        ),
        "subject": clean_text(
            get_field(payload, ["subject", "subject_name", "Subject", "Subject Name"])
        ),
        "topic": clean_text(get_field(payload, ["topic", "Topic", "category"])),
        "choice_type": "single",
    }

    reason = validate_sample(sample)
    if reason:
        return None, reason

    # Always trust the normalized option text for the final answer text.
    sample["answer_text"] = sample["options"][sample["answer"]]
    return sample, None


def convert_splits(
    split_records: dict[str, list[dict[str, Any]]]
) -> tuple[dict[str, list[dict[str, Any]]], Counter[str]]:
    converted = {split: [] for split in CANONICAL_SPLITS}
    dropped_reasons: Counter[str] = Counter()

    for split in CANONICAL_SPLITS:
        next_index = 1
        for record in split_records.get(split, []):
            sample, reason = convert_record(record, split, next_index)
            if sample is None:
                dropped_reasons[reason or "unknown"] += 1
                continue

            converted[split].append(sample)
            next_index += 1

    return converted, dropped_reasons


def write_jsonl(path: Path, samples: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        for sample in samples:
            file.write(json.dumps(sample, ensure_ascii=False) + "\n")


def write_outputs(output_dir: Path, converted: dict[str, list[dict[str, Any]]]) -> None:
    for split in CANONICAL_SPLITS:
        write_jsonl(output_dir / f"medqa_{split}.jsonl", converted[split])


def preview_samples(
    converted: dict[str, list[dict[str, Any]]],
    limit: int = 3,
) -> list[dict[str, Any]]:
    preview: list[dict[str, Any]] = []
    for split in CANONICAL_SPLITS:
        for sample in converted[split]:
            preview.append(sample)
            if len(preview) >= limit:
                return preview
    return preview


def write_stats(
    stats_path: Path,
    raw_total: int,
    considered_total: int,
    converted: dict[str, list[dict[str, Any]]],
    dropped_reasons: Counter[str],
    seed: int,
    max_samples: int,
) -> None:
    stats_path.parent.mkdir(parents=True, exist_ok=True)

    filtered_total = sum(len(samples) for samples in converted.values())
    dropped_total = sum(dropped_reasons.values())
    preview = preview_samples(converted)

    lines = [
        "# MedQA 数据处理统计",
        "",
        f"- 数据集来源：`{DATASET_NAME}`",
        f"- 随机种子：`{seed}`",
        f"- max_samples：`{max_samples}`",
        f"- 原始样本数：{raw_total}",
        f"- 本次处理样本数：{considered_total}",
        f"- 过滤后样本数：{filtered_total}",
        f"- 被过滤样本数量：{dropped_total}",
        "",
        "## 各 split 样本数",
        "",
    ]

    for split in CANONICAL_SPLITS:
        lines.append(f"- {split}：{len(converted[split])}")

    lines.extend(["", "## 过滤原因", ""])
    if dropped_reasons:
        for reason, count in dropped_reasons.most_common():
            lines.append(f"- {reason}：{count}")
    else:
        lines.append("- 无")

    lines.extend(["", "## 前 3 条样本预览", ""])
    if preview:
        for index, sample in enumerate(preview, start=1):
            lines.append(f"### 样本 {index}")
            lines.append("")
            lines.append("```json")
            lines.append(json.dumps(sample, ensure_ascii=False, indent=2))
            lines.append("```")
            lines.append("")
    else:
        lines.append("无可预览样本。")

    stats_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def prepare_medqa(args: argparse.Namespace) -> None:
    dataset = load_medqa_dataset()
    raw_items = dataset_items(dataset)
    raw_total = len(raw_items)

    if args.max_samples > 0:
        raw_items = raw_items[: args.max_samples]

    split_records = split_examples(raw_items, args.seed)
    converted, dropped_reasons = convert_splits(split_records)

    write_outputs(args.output_dir, converted)
    write_stats(
        stats_path=args.stats_path,
        raw_total=raw_total,
        considered_total=len(raw_items),
        converted=converted,
        dropped_reasons=dropped_reasons,
        seed=args.seed,
        max_samples=args.max_samples,
    )

    print(f"MedQA processed files written to: {args.output_dir}")
    print(f"MedQA stats written to: {args.stats_path}")
    for split in CANONICAL_SPLITS:
        print(f"{split}: {len(converted[split])}")


def main() -> None:
    args = parse_args()
    try:
        prepare_medqa(args)
    except KeyboardInterrupt:
        raise
    except Exception as exc:
        print(f"[prepare_medqa] 运行失败：{exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
