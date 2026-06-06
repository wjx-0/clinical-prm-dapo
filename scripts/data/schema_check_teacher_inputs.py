"""Validate teacher input candidate JSONL files."""

from __future__ import annotations

import argparse
import json
import re
import string
import sys
from collections import Counter
from pathlib import Path
from typing import Any


LETTERS = ("A", "B", "C", "D")
VALID_SOURCES = {"medqa", "medmcqa"}
VALID_SPLITS = {"train", "dev"}
VALID_QUALITIES = {"none", "low", "medium", "high"}
REQUIRED_FIELDS = (
    "id",
    "source",
    "split",
    "question",
    "options",
    "answer",
    "answer_text",
    "explanation",
    "subject",
    "topic",
    "input_quality",
)
REQUIRED_QUALITY_FIELDS = (
    "has_explanation",
    "explanation_len",
    "explanation_quality",
    "question_len",
    "option_duplicate",
    "dirty_text",
)
DEFAULT_FILES = (
    "teacher_sft_train_inputs.jsonl",
    "teacher_sft_dev_inputs.jsonl",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate teacher input candidates.")
    parser.add_argument("--input_dir", type=Path, default=Path("data/teacher_inputs"))
    parser.add_argument(
        "--error_output",
        type=Path,
        default=Path("outputs/data_validation/teacher_input_errors.jsonl"),
    )
    parser.add_argument(
        "--report_path",
        type=Path,
        default=Path("docs/teacher_input_validation_report.md"),
    )
    return parser.parse_args()


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return re.sub(r"\s+", " ", value).strip()
    return re.sub(r"\s+", " ", str(value)).strip()


def normalize_question(value: Any) -> str:
    text = clean_text(value).lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = re.sub(r"[^\w\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


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


def validate_options(sample: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    options = sample.get("options")
    if not isinstance(options, dict):
        return ["options is not a dict"]
    for letter in LETTERS:
        if letter not in options:
            errors.append(f"missing option: {letter}")
        elif not clean_text(options.get(letter)):
            errors.append(f"empty option: {letter}")
    return errors


def validate_input_quality(sample: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    quality = sample.get("input_quality")
    if not isinstance(quality, dict):
        return ["input_quality is not a dict"]

    for field in REQUIRED_QUALITY_FIELDS:
        if field not in quality:
            errors.append(f"missing input_quality field: {field}")

    if "has_explanation" in quality and not isinstance(quality["has_explanation"], bool):
        errors.append("input_quality.has_explanation is not bool")
    if "option_duplicate" in quality and not isinstance(quality["option_duplicate"], bool):
        errors.append("input_quality.option_duplicate is not bool")
    if "dirty_text" in quality and not isinstance(quality["dirty_text"], bool):
        errors.append("input_quality.dirty_text is not bool")
    if "explanation_len" in quality:
        if not isinstance(quality["explanation_len"], int) or quality["explanation_len"] < 0:
            errors.append("input_quality.explanation_len is not a non-negative int")
    if "question_len" in quality:
        if not isinstance(quality["question_len"], int) or quality["question_len"] <= 0:
            errors.append("input_quality.question_len is not a positive int")
    if quality.get("explanation_quality") not in VALID_QUALITIES:
        errors.append(f"invalid explanation_quality: {quality.get('explanation_quality')}")

    return errors


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

    if split == "test":
        errors.append("test split is not allowed")

    if not clean_text(sample.get("question")):
        errors.append("question is empty or not a string")

    errors.extend(validate_options(sample))

    answer = sample.get("answer")
    options = sample.get("options") if isinstance(sample.get("options"), dict) else {}
    if answer not in LETTERS:
        errors.append(f"invalid answer: {answer}")
    elif sample.get("answer_text") != options.get(answer):
        errors.append("answer_text does not equal options[answer]")

    errors.extend(validate_input_quality(sample))
    return errors


def empty_file_stats() -> dict[str, Any]:
    return {
        "count": 0,
        "errors": 0,
        "source": Counter(),
        "answer": Counter(),
        "explanation_quality": Counter(),
        "dirty_text": 0,
    }


def update_stats(stats: dict[str, Any], sample: dict[str, Any]) -> None:
    stats["count"] += 1
    stats["source"][sample.get("source") or "unknown"] += 1
    stats["answer"][sample.get("answer") or "unknown"] += 1
    quality = sample.get("input_quality") if isinstance(sample.get("input_quality"), dict) else {}
    stats["explanation_quality"][quality.get("explanation_quality") or "unknown"] += 1
    if quality.get("dirty_text"):
        stats["dirty_text"] += 1


def add_error(
    errors: list[dict[str, Any]],
    path: Path,
    line_no: int,
    sample: dict[str, Any],
    sample_errors: list[str],
) -> None:
    errors.append(
        {
            "file": str(path),
            "line_no": line_no,
            "id": sample.get("id", ""),
            "errors": sample_errors,
            "sample": sample,
        }
    )


def validate_files(input_dir: Path) -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    file_stats: dict[str, dict[str, Any]] = {}
    errors: list[dict[str, Any]] = []
    seen_ids: dict[str, tuple[Path, int, str]] = {}
    seen_questions: dict[str, tuple[Path, int, str]] = {}
    duplicate_id_count = 0
    duplicate_question_count = 0

    for file_name in DEFAULT_FILES:
        path = input_dir / file_name
        stats = empty_file_stats()
        file_stats[file_name] = stats
        if not path.exists():
            print(f"WARNING: missing teacher input file: {path}", file=sys.stderr)
            continue

        for line_no, sample, json_error in read_jsonl(path):
            if json_error:
                stats["count"] += 1
                stats["errors"] += 1
                add_error(errors, path, line_no, {}, [json_error])
                continue

            sample_errors = validate_sample(sample)
            sample_id = clean_text(sample.get("id"))
            split = clean_text(sample.get("split"))
            normalized_question = normalize_question(sample.get("question"))

            if sample_id:
                previous = seen_ids.get(sample_id)
                if previous is not None:
                    duplicate_id_count += 1
                    sample_errors.append(f"duplicate id with {previous[0]}:{previous[1]}")
                else:
                    seen_ids[sample_id] = (path, line_no, split)

            if normalized_question:
                previous = seen_questions.get(normalized_question)
                if previous is not None:
                    duplicate_question_count += 1
                    sample_errors.append(
                        f"duplicate normalized question with {previous[0]}:{previous[1]}"
                    )
                else:
                    seen_questions[normalized_question] = (path, line_no, split)

            if sample_errors:
                stats["errors"] += 1
                add_error(errors, path, line_no, sample, sample_errors)

            update_stats(stats, sample)

    duplicate_stats = {
        "duplicate_id_count": duplicate_id_count,
        "duplicate_question_count": duplicate_question_count,
    }
    return file_stats, errors, duplicate_stats


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        for row in rows:
            file.write(json.dumps(row, ensure_ascii=False) + "\n")


def merge_counter(file_stats: dict[str, dict[str, Any]], key: str) -> Counter[Any]:
    merged: Counter[Any] = Counter()
    for stats in file_stats.values():
        merged.update(stats[key])
    return merged


def counter_to_lines(counter: Counter[Any], empty_label: str = "<EMPTY>") -> list[str]:
    if not counter:
        return ["- 无"]
    return [f"- `{key if key else empty_label}`：{value}" for key, value in counter.most_common()]


def write_report(
    path: Path,
    file_stats: dict[str, dict[str, Any]],
    errors: list[dict[str, Any]],
    duplicate_stats: dict[str, Any],
) -> None:
    source_counts = merge_counter(file_stats, "source")
    answer_counts = merge_counter(file_stats, "answer")
    quality_counts = merge_counter(file_stats, "explanation_quality")
    dirty_count = sum(stats["dirty_text"] for stats in file_stats.values())
    validation_passed = len(errors) == 0

    lines = [
        "# Teacher Input 校验报告",
        "",
        "## 样本数",
        "",
    ]
    for file_name, stats in file_stats.items():
        split = "train" if "train" in file_name else "dev"
        lines.append(f"- {split}：{stats['count']}（错误 {stats['errors']}）")
    lines.extend(
        [
            "",
            "## source 分布",
            "",
            *counter_to_lines(source_counts),
            "",
            "## answer 分布",
            "",
            *counter_to_lines(answer_counts),
            "",
            "## explanation_quality 分布",
            "",
            *counter_to_lines(quality_counts),
            "",
            "## dirty_text 数量",
            "",
            f"- dirty_text：{dirty_count}",
            "",
            "## 去重检查",
            "",
            f"- train/dev 重复 id 数量：{duplicate_stats['duplicate_id_count']}",
            f"- train/dev 重复 normalized question 数量：{duplicate_stats['duplicate_question_count']}",
            "",
            "## validation 是否通过",
            "",
            f"- {'通过' if validation_passed else '未通过'}",
        ]
    )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def print_summary(
    file_stats: dict[str, dict[str, Any]],
    errors: list[dict[str, Any]],
    duplicate_stats: dict[str, Any],
    report_path: Path,
) -> None:
    print("Teacher input validation summary:")
    for file_name, stats in file_stats.items():
        print(f"  {file_name}: samples={stats['count']}, errors={stats['errors']}")
    print(f"  duplicate ids: {duplicate_stats['duplicate_id_count']}")
    print(f"  duplicate questions: {duplicate_stats['duplicate_question_count']}")
    print(f"  validation passed: {len(errors) == 0}")
    print(f"  report: {report_path}")


def main() -> None:
    args = parse_args()
    try:
        file_stats, errors, duplicate_stats = validate_files(args.input_dir)
        write_jsonl(args.error_output, errors)
        write_report(args.report_path, file_stats, errors, duplicate_stats)
        print_summary(file_stats, errors, duplicate_stats, args.report_path)
        if errors:
            raise SystemExit(1)
    except SystemExit:
        raise
    except Exception as exc:  # noqa: BLE001 - CLI should surface a clear failure.
        raise SystemExit(f"ERROR: failed to validate teacher inputs: {exc}") from exc


if __name__ == "__main__":
    main()
