"""Prepare MedMCQA into normalized multiple-choice QA JSONL files.

This script only builds the processed QA layer. It does not create SFT, PRM,
or RL training data.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


DATASET_NAME = "openlifescienceai/medmcqa"
LETTERS = ("A", "B", "C", "D")
ZERO_BASED_COP_TO_LETTER = {0: "A", 1: "B", 2: "C", 3: "D"}
ONE_BASED_COP_TO_LETTER = {1: "A", 2: "B", 3: "C", 4: "D"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert openlifescienceai/medmcqa to processed QA JSONL."
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
        default=Path("docs/data_stats_medmcqa.md"),
        help="Markdown path for MedMCQA data statistics.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Reserved for compatibility. MedMCQA uses source splits directly.",
    )
    parser.add_argument(
        "--max_samples",
        type=int,
        default=-1,
        help="Debug limit. If positive, process at most N rows per source split.",
    )
    return parser.parse_args()


def load_medmcqa_dataset() -> Any:
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


def get_field(record: dict[str, Any], candidates: list[str]) -> Any:
    normalized = {normalize_key(key): value for key, value in record.items()}
    for candidate in candidates:
        key = normalize_key(candidate)
        if key in normalized:
            return normalized[key]
    return None


def normalize_split_name(split_name: str) -> str | None:
    name = split_name.lower()
    if name == "train":
        return "train"
    if name in {"validation", "valid", "dev"}:
        return "dev"
    if name == "test":
        return "test"
    return None


def parse_cop(value: Any) -> int | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)

    text = clean_text(value)
    if re.fullmatch(r"-?\d+", text):
        return int(text)
    if re.fullmatch(r"-?\d+\.0", text):
        return int(float(text))
    return None


def infer_cop_mapping(dataset: Any, max_per_split: int = 5000) -> dict[int, str]:
    """Infer whether MedMCQA stores ``cop`` as 0-based or 1-based.

    The public ``openlifescienceai/medmcqa`` data currently uses 0/1/2/3 for
    labeled samples and -1 for the unlabeled test split, while some references
    describe it as 1/2/3/4. Supporting both prevents silent answer corruption.
    """
    observed: Counter[int] = Counter()
    for split_name in dataset.keys():
        for index, record in enumerate(dataset[split_name]):
            if index >= max_per_split:
                break
            cop = parse_cop(get_field(dict(record), ["cop", "correct_option", "answer_idx"]))
            if cop is not None and cop >= 0:
                observed[cop] += 1

    if 0 in observed:
        return ZERO_BASED_COP_TO_LETTER
    return ONE_BASED_COP_TO_LETTER


def normalize_choice_type(value: Any) -> str:
    return clean_text(value).lower()


def validate_sample(sample: dict[str, Any]) -> str | None:
    if sample["answer"] not in LETTERS:
        return "invalid_cop"
    if not sample["question"]:
        return "question_empty"
    if any(not clean_text(sample["options"].get(letter)) for letter in LETTERS):
        return "option_empty"
    if not sample["answer_text"]:
        return "answer_text_empty"
    return None


def validate_unlabeled_sample(sample: dict[str, Any]) -> str | None:
    if not sample["question"]:
        return "question_empty"
    if any(not clean_text(sample["options"].get(letter)) for letter in LETTERS):
        return "option_empty"
    return None


def build_base_sample(
    record: dict[str, Any],
    split: str,
    index: int,
    answer: str,
) -> dict[str, Any]:
    original_choice_type = normalize_choice_type(get_field(record, ["choice_type"]))
    options = {
        "A": clean_text(get_field(record, ["opa", "option_a", "A"])),
        "B": clean_text(get_field(record, ["opb", "option_b", "B"])),
        "C": clean_text(get_field(record, ["opc", "option_c", "C"])),
        "D": clean_text(get_field(record, ["opd", "option_d", "D"])),
    }

    return {
        "id": f"medmcqa_{split}_{index:06d}",
        "source": "medmcqa",
        "split": split,
        "language": "en",
        "question": clean_text(get_field(record, ["question", "Question"])),
        "options": options,
        "answer": answer,
        "answer_text": options.get(answer, "") if answer else "",
        "explanation": clean_text(get_field(record, ["exp", "explanation"])),
        "subject": clean_text(get_field(record, ["subject_name", "subject"])),
        "topic": clean_text(get_field(record, ["topic_name", "topic"])),
        "choice_type": "single",
        "original_choice_type": original_choice_type,
    }


def convert_record(
    record: dict[str, Any],
    split: str,
    index: int,
    cop_to_letter: dict[int, str],
) -> tuple[dict[str, Any] | None, str | None]:
    cop = parse_cop(get_field(record, ["cop", "correct_option", "answer_idx"]))
    answer = cop_to_letter.get(cop) if cop is not None else ""
    sample = build_base_sample(record, split, index, answer)

    reason = validate_sample(sample)
    if reason:
        return None, reason

    sample["answer_text"] = sample["options"][sample["answer"]]
    return sample, None


def convert_unlabeled_record(
    record: dict[str, Any],
    split: str,
    index: int,
) -> tuple[dict[str, Any] | None, str | None]:
    sample = build_base_sample(record, split, index, answer="")
    reason = validate_unlabeled_sample(sample)
    if reason:
        return None, reason
    return sample, None


def split_length(split_data: Any) -> int:
    try:
        return len(split_data)
    except TypeError:
        return -1


def iter_limited(split_data: Any, max_samples: int) -> Any:
    for index, record in enumerate(split_data):
        if max_samples > 0 and index >= max_samples:
            break
        yield dict(record)


def convert_dataset(
    dataset: Any,
    max_samples: int,
) -> tuple[
    dict[str, list[dict[str, Any]]],
    dict[str, list[dict[str, Any]]],
    Counter[str],
    Counter[str],
    Counter[str],
]:
    converted: dict[str, list[dict[str, Any]]] = defaultdict(list)
    unlabeled: dict[str, list[dict[str, Any]]] = defaultdict(list)
    raw_split_counts: Counter[str] = Counter()
    filtered_reasons: Counter[str] = Counter()
    subject_counts: Counter[str] = Counter()
    next_indices: Counter[str] = Counter()
    next_unlabeled_indices: Counter[str] = Counter()

    if not hasattr(dataset, "keys"):
        raise RuntimeError("MedMCQA 数据集应为 DatasetDict，但当前返回值没有 split。")

    cop_to_letter = infer_cop_mapping(dataset)

    for raw_split in dataset.keys():
        split_data = dataset[raw_split]
        raw_split_counts[str(raw_split)] = split_length(split_data)
        split = normalize_split_name(str(raw_split))
        if split is None:
            filtered_reasons["unknown_split"] += max(split_length(split_data), 0)
            continue

        converted.setdefault(split, [])
        for record in iter_limited(split_data, max_samples):
            next_index = next_indices[split] + 1
            sample, reason = convert_record(record, split, next_index, cop_to_letter)
            if sample is None:
                cop = parse_cop(get_field(record, ["cop", "correct_option", "answer_idx"]))
                if split == "test" and cop == -1:
                    next_unlabeled_index = next_unlabeled_indices[split] + 1
                    unlabeled_sample, unlabeled_reason = convert_unlabeled_record(
                        record,
                        split,
                        next_unlabeled_index,
                    )
                    if unlabeled_sample is not None:
                        next_unlabeled_indices[split] = next_unlabeled_index
                        unlabeled[split].append(unlabeled_sample)
                        continue
                    filtered_reasons[f"unlabeled_{unlabeled_reason or 'unknown'}"] += 1
                    continue

                filtered_reasons[reason or "unknown"] += 1
                continue

            next_indices[split] = next_index
            converted[split].append(sample)
            subject = sample["subject"] or "<EMPTY>"
            subject_counts[subject] += 1

    return dict(converted), dict(unlabeled), raw_split_counts, filtered_reasons, subject_counts


def write_jsonl(path: Path, samples: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        for sample in samples:
            file.write(json.dumps(sample, ensure_ascii=False) + "\n")


def write_outputs(
    output_dir: Path,
    converted: dict[str, list[dict[str, Any]]],
    unlabeled: dict[str, list[dict[str, Any]]],
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for split in ("train", "dev", "test"):
        if split not in converted:
            continue
        write_jsonl(output_dir / f"medmcqa_{split}.jsonl", converted[split])
    for split, samples in unlabeled.items():
        write_jsonl(output_dir / f"medmcqa_{split}_unlabeled.jsonl", samples)


def preview_samples(converted: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    preview: list[dict[str, Any]] = []
    for split in ("train", "dev", "test"):
        for sample in converted.get(split, []):
            preview.append(sample)
            if len(preview) >= 3:
                return preview
    return preview


def write_stats(
    stats_path: Path,
    raw_split_counts: Counter[str],
    converted: dict[str, list[dict[str, Any]]],
    unlabeled: dict[str, list[dict[str, Any]]],
    filtered_reasons: Counter[str],
    subject_counts: Counter[str],
    seed: int,
    max_samples: int,
) -> None:
    stats_path.parent.mkdir(parents=True, exist_ok=True)
    preview = preview_samples(converted)

    lines = [
        "# MedMCQA 数据处理统计",
        "",
        f"- 数据集来源：`{DATASET_NAME}`",
        f"- 随机种子：`{seed}`",
        f"- max_samples：`{max_samples}`",
        "",
        "## 原始 split 样本数",
        "",
    ]

    for split, count in raw_split_counts.items():
        lines.append(f"- {split}：{count}")

    lines.extend(["", "## 输出 split 过滤后样本数", ""])
    for split in ("train", "dev", "test"):
        lines.append(f"- {split}：{len(converted.get(split, []))}")

    lines.extend(["", "## 无答案样本输出数", ""])
    for split in ("train", "dev", "test"):
        lines.append(f"- {split}_unlabeled：{len(unlabeled.get(split, []))}")

    lines.extend(["", "## 过滤原因统计", ""])
    if filtered_reasons:
        for reason, count in filtered_reasons.most_common():
            lines.append(f"- {reason}：{count}")
    else:
        lines.append("- 无")

    lines.extend(["", "## Subject 分布 Top 20", ""])
    if subject_counts:
        for subject, count in subject_counts.most_common(20):
            lines.append(f"- {subject}：{count}")
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


def prepare_medmcqa(args: argparse.Namespace) -> None:
    dataset = load_medmcqa_dataset()
    converted, unlabeled, raw_split_counts, filtered_reasons, subject_counts = convert_dataset(
        dataset=dataset,
        max_samples=args.max_samples,
    )

    write_outputs(args.output_dir, converted, unlabeled)
    write_stats(
        stats_path=args.stats_path,
        raw_split_counts=raw_split_counts,
        converted=converted,
        unlabeled=unlabeled,
        filtered_reasons=filtered_reasons,
        subject_counts=subject_counts,
        seed=args.seed,
        max_samples=args.max_samples,
    )

    print(f"MedMCQA processed files written to: {args.output_dir}")
    print(f"MedMCQA stats written to: {args.stats_path}")
    for split in ("train", "dev", "test"):
        print(f"{split}: {len(converted.get(split, []))}")
    for split in ("train", "dev", "test"):
        count = len(unlabeled.get(split, []))
        if count:
            print(f"{split}_unlabeled: {count}")


def main() -> None:
    args = parse_args()
    try:
        prepare_medmcqa(args)
    except KeyboardInterrupt:
        raise
    except Exception as exc:
        print(f"[prepare_medmcqa] 运行失败：{exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
