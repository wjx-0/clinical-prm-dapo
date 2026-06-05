"""Validate processed multiple-choice QA JSONL files."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


REQUIRED_FIELDS = (
    "id",
    "source",
    "split",
    "language",
    "question",
    "options",
    "answer",
    "answer_text",
    "explanation",
    "subject",
    "topic",
    "choice_type",
)
VALID_SOURCES = {"medqa", "medmcqa"}
VALID_SPLITS = {"train", "dev", "test"}
LETTERS = ("A", "B", "C", "D")
DEFAULT_FILES = (
    "medqa_train.jsonl",
    "medqa_dev.jsonl",
    "medqa_test.jsonl",
    "medmcqa_train.jsonl",
    "medmcqa_dev.jsonl",
    "medmcqa_test.jsonl",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check processed QA JSONL files for schema consistency."
    )
    parser.add_argument(
        "--input_dir",
        type=Path,
        default=Path("data/processed"),
        help="Directory containing processed QA JSONL files.",
    )
    parser.add_argument(
        "--error_output",
        type=Path,
        default=Path("outputs/data_validation/processed_errors.jsonl"),
        help="Path for invalid samples.",
    )
    parser.add_argument(
        "--report_path",
        type=Path,
        default=Path("docs/data_stats_processed.md"),
        help="Markdown report path.",
    )
    return parser.parse_args()


def clean_text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def read_jsonl(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as file:
        for line_no, line in enumerate(file, start=1):
            text = line.strip()
            if not text:
                continue
            try:
                yield line_no, json.loads(text), None
            except json.JSONDecodeError as exc:
                yield line_no, {}, f"invalid json: {exc.msg}"


def validate_sample(sample: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    for field in REQUIRED_FIELDS:
        if field not in sample:
            errors.append(f"missing field: {field}")

    source = sample.get("source")
    if source not in VALID_SOURCES:
        errors.append(f"invalid source: {source}")

    split = sample.get("split")
    if split not in VALID_SPLITS:
        errors.append(f"invalid split: {split}")

    if sample.get("language") != "en":
        errors.append(f"invalid language: {sample.get('language')}")

    if not clean_text(sample.get("question")):
        errors.append("question is empty or not a string")

    options = sample.get("options")
    if not isinstance(options, dict):
        errors.append("options is not a dict")
        options = {}

    for letter in LETTERS:
        if letter not in options:
            errors.append(f"missing option: {letter}")
        elif not clean_text(options.get(letter)):
            errors.append(f"empty option: {letter}")

    answer = sample.get("answer")
    if answer not in LETTERS:
        errors.append(f"invalid answer: {answer}")
    elif isinstance(options, dict) and sample.get("answer_text") != options.get(answer):
        errors.append("answer_text does not equal options[answer]")

    if sample.get("choice_type") != "single":
        errors.append(f"invalid choice_type: {sample.get('choice_type')}")

    return errors


def string_length(value: Any) -> int:
    return len(value.strip()) if isinstance(value, str) else 0


def update_summary(
    summary: dict[str, Any],
    file_name: str,
    sample: dict[str, Any],
) -> None:
    source = sample.get("source")
    split = sample.get("split")
    answer = sample.get("answer")

    summary["file_counts"][file_name] += 1
    if source:
        summary["source_counts"][source] += 1
    if split:
        summary["split_counts"][split] += 1
    if source and split:
        summary["dataset_split_counts"][(source, split)] += 1
    if answer:
        summary["answer_counts"][answer] += 1
    if source == "medmcqa":
        subject = clean_text(sample.get("subject")) or "<EMPTY>"
        summary["medmcqa_subject_counts"][subject] += 1


def update_file_stats(stats: dict[str, Any], sample: dict[str, Any]) -> None:
    stats["sample_count"] += 1
    if sample.get("source"):
        stats["source_counts"][sample.get("source")] += 1
    if sample.get("answer"):
        stats["answer_counts"][sample.get("answer")] += 1

    stats["question_chars"] += string_length(sample.get("question"))
    options = sample.get("options")
    if isinstance(options, dict):
        for letter in LETTERS:
            stats["option_chars"] += string_length(options.get(letter))
            stats["option_count"] += 1


def empty_file_stats() -> dict[str, Any]:
    return {
        "sample_count": 0,
        "error_count": 0,
        "source_counts": Counter(),
        "answer_counts": Counter(),
        "question_chars": 0,
        "option_chars": 0,
        "option_count": 0,
    }


def validate_file(
    path: Path,
    summary: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    stats = empty_file_stats()
    errors: list[dict[str, Any]] = []

    for line_no, sample, json_error in read_jsonl(path):
        if json_error:
            stats["sample_count"] += 1
            stats["error_count"] += 1
            errors.append(
                {
                    "file": str(path),
                    "line_no": line_no,
                    "id": "",
                    "errors": [json_error],
                    "sample": {},
                }
            )
            continue

        sample_errors = validate_sample(sample)
        if sample_errors:
            stats["error_count"] += 1
            errors.append(
                {
                    "file": str(path),
                    "line_no": line_no,
                    "id": sample.get("id", ""),
                    "errors": sample_errors,
                    "sample": sample,
                }
            )
        else:
            update_summary(summary, path.name, sample)

        update_file_stats(stats, sample)

    return stats, errors


def write_errors(path: Path, errors: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        for error in errors:
            file.write(json.dumps(error, ensure_ascii=False) + "\n")


def print_file_summary(file_name: str, stats: dict[str, Any]) -> None:
    sample_count = stats["sample_count"]
    option_count = stats["option_count"]
    avg_question_len = stats["question_chars"] / sample_count if sample_count else 0.0
    avg_option_len = stats["option_chars"] / option_count if option_count else 0.0

    print(f"\n{file_name}")
    print(f"  样本数: {sample_count}")
    print(f"  错误样本数: {stats['error_count']}")
    print(f"  source 分布: {dict(stats['source_counts'])}")
    print(f"  answer 分布: {dict(stats['answer_counts'])}")
    print(f"  平均 question 长度: {avg_question_len:.2f}")
    print(f"  平均 option 长度: {avg_option_len:.2f}")


def format_counter(counter: Counter[Any]) -> list[str]:
    if not counter:
        return ["- 无"]
    return [f"- {key}：{value}" for key, value in counter.most_common()]


def write_report(
    report_path: Path,
    summary: dict[str, Any],
    missing_files: list[str],
    total_errors: int,
) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    total_samples = sum(summary["file_counts"].values())
    passed = total_errors == 0

    lines = [
        "# Processed QA 数据统计",
        "",
        "## 文件样本数",
        "",
    ]

    for file_name in DEFAULT_FILES:
        lines.append(f"- {file_name}：{summary['file_counts'].get(file_name, 0)}")

    lines.extend(["", "## MedQA train/dev/test 样本数", ""])
    for split in ("train", "dev", "test"):
        lines.append(f"- {split}：{summary['dataset_split_counts'].get(('medqa', split), 0)}")

    lines.extend(["", "## MedMCQA train/dev/test 样本数", ""])
    for split in ("train", "dev", "test"):
        lines.append(f"- {split}：{summary['dataset_split_counts'].get(('medmcqa', split), 0)}")

    lines.extend(
        [
            "",
            f"## 总样本数",
            "",
            f"- 总样本数：{total_samples}",
            "",
            "## 各 source 样本数",
            "",
        ]
    )
    lines.extend(format_counter(summary["source_counts"]))

    lines.extend(["", "## 各 split 样本数", ""])
    lines.extend(format_counter(summary["split_counts"]))

    lines.extend(["", "## answer 分布", ""])
    lines.extend(format_counter(summary["answer_counts"]))

    lines.extend(["", "## MedMCQA subject Top 20", ""])
    subject_top20 = Counter(dict(summary["medmcqa_subject_counts"].most_common(20)))
    lines.extend(format_counter(subject_top20))

    lines.extend(["", "## 缺失文件", ""])
    if missing_files:
        for file_name in missing_files:
            lines.append(f"- {file_name}")
    else:
        lines.append("- 无")

    lines.extend(
        [
            "",
            "## Validation 结果",
            "",
            f"- 是否通过：{'通过' if passed else '未通过'}",
            f"- 错误样本数：{total_errors}",
        ]
    )

    report_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def initial_summary() -> dict[str, Any]:
    return {
        "file_counts": Counter(),
        "source_counts": Counter(),
        "split_counts": Counter(),
        "dataset_split_counts": Counter(),
        "answer_counts": Counter(),
        "medmcqa_subject_counts": Counter(),
    }


def schema_check(args: argparse.Namespace) -> None:
    summary = initial_summary()
    all_errors: list[dict[str, Any]] = []
    missing_files: list[str] = []

    for file_name in DEFAULT_FILES:
        path = args.input_dir / file_name
        if not path.exists():
            print(f"WARNING: missing file: {path}", file=sys.stderr)
            missing_files.append(file_name)
            continue

        stats, errors = validate_file(path, summary)
        all_errors.extend(errors)
        print_file_summary(file_name, stats)

    write_errors(args.error_output, all_errors)
    write_report(
        report_path=args.report_path,
        summary=summary,
        missing_files=missing_files,
        total_errors=len(all_errors),
    )

    print(f"\n错误样本输出: {args.error_output}")
    print(f"统计报告输出: {args.report_path}")
    if all_errors:
        print(f"Validation failed: {len(all_errors)} invalid samples.", file=sys.stderr)
    else:
        print("Validation passed.")


def main() -> None:
    args = parse_args()
    try:
        schema_check(args)
    except KeyboardInterrupt:
        raise
    except Exception as exc:
        print(f"[schema_check_processed] 运行失败：{exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
