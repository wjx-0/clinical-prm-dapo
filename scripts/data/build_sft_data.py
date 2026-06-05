"""Build LLaMA-Factory Alpaca-style SFT data from processed QA JSONL."""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


INSTRUCTION = (
    "Please solve the following medical multiple-choice question with "
    "step-by-step reasoning. Put your reasoning inside <think></think> and "
    "the final answer inside <answer></answer>."
)
LETTERS = ("A", "B", "C", "D")
DEFAULT_SOURCES = ("medqa", "medmcqa")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build Alpaca-style SFT data from processed QA files."
    )
    parser.add_argument("--input_dir", type=Path, default=Path("data/processed"))
    parser.add_argument("--output_dir", type=Path, default=Path("data/sft"))
    parser.add_argument("--stats_path", type=Path, default=Path("docs/data_stats_sft.md"))
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--max_samples", type=int, default=-1)
    parser.add_argument("--sources", nargs="+", default=list(DEFAULT_SOURCES))
    parser.add_argument("--train_files", nargs="*", default=None)
    parser.add_argument("--dev_files", nargs="*", default=None)
    return parser.parse_args()


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return re.sub(r"\s+", " ", value).strip()
    return re.sub(r"\s+", " ", str(value)).strip()


def default_files(input_dir: Path, sources: list[str], split: str) -> list[Path]:
    return [input_dir / f"{source}_{split}.jsonl" for source in sources]


def parse_file_args(files: list[str] | None, input_dir: Path) -> list[Path] | None:
    if files is None:
        return None
    parsed = []
    for file_name in files:
        path = Path(file_name)
        parsed.append(path if path.is_absolute() else input_dir / path)
    return parsed


def read_jsonl(path: Path, max_samples: int) -> list[dict[str, Any]]:
    if not path.exists():
        print(f"WARNING: missing input file: {path}", file=sys.stderr)
        return []

    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as file:
        for line_no, line in enumerate(file, start=1):
            if max_samples > 0 and len(rows) >= max_samples:
                break
            text = line.strip()
            if not text:
                continue
            try:
                rows.append(json.loads(text))
            except json.JSONDecodeError as exc:
                raise RuntimeError(f"Invalid JSON in {path}:{line_no}: {exc}") from exc
    return rows


def format_input(sample: dict[str, Any]) -> str:
    options = sample["options"]
    return (
        "Question:\n"
        f"{clean_text(sample['question'])}\n\n"
        "Options:\n"
        f"A. {clean_text(options['A'])}\n"
        f"B. {clean_text(options['B'])}\n"
        f"C. {clean_text(options['C'])}\n"
        f"D. {clean_text(options['D'])}"
    )


def split_explanation(explanation: str) -> list[str]:
    text = clean_text(explanation)
    if not text:
        return []

    parts = re.split(r"(?<=[.!?])\s+|\s*;\s+", text)
    cleaned = [part.strip(" -") for part in parts if clean_text(part)]
    if not cleaned:
        return [text]
    return cleaned


def truncate_sentence(sentence: str, max_chars: int = 220) -> str:
    text = clean_text(sentence)
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 3].rstrip() + "..."


def build_reasoning_steps(sample: dict[str, Any]) -> list[str]:
    answer = sample["answer"]
    answer_text = clean_text(sample["answer_text"])
    explanation = clean_text(sample.get("explanation", ""))

    if explanation:
        pieces = split_explanation(explanation)
        evidence = truncate_sentence(pieces[0]) if pieces else "The explanation supports the selected option."
        detail = (
            truncate_sentence(pieces[1])
            if len(pieces) > 1
            else f"This evidence points to option {answer}: {answer_text}."
        )
        return [
            "Step 1: Identify the key medical clues and the decision being asked in the question.",
            f"Step 2: Use the provided explanation to focus on the relevant evidence: {evidence}",
            f"Step 3: Compare the options and select the choice best supported by that evidence: {detail}",
            f"Step 4: Therefore, the best answer is {answer}.",
        ]

    return [
        "Step 1: Identify the key clinical information in the question.",
        "Step 2: Compare the options based on the given information.",
        "Step 3: Select the option that best matches the question stem.",
        f"Step 4: Therefore, the best answer is {answer}.",
    ]


def build_output(sample: dict[str, Any]) -> str:
    steps = build_reasoning_steps(sample)
    return "<think>\n" + "\n".join(steps) + "\n</think>\n" + f"<answer>{sample['answer']}</answer>"


def extract_answer_tag(output: str) -> str | None:
    matches = re.findall(r"<answer>\s*([A-D])\s*</answer>", output)
    if len(matches) != 1:
        return None
    return matches[0]


def validate_processed_sample(sample: dict[str, Any]) -> str | None:
    options = sample.get("options")
    if not clean_text(sample.get("question")):
        return "empty_question"
    if not isinstance(options, dict):
        return "invalid_options"
    for letter in LETTERS:
        if not clean_text(options.get(letter)):
            return f"empty_option_{letter}"
    if sample.get("answer") not in LETTERS:
        return "invalid_answer"
    if sample.get("answer_text") != options.get(sample.get("answer")):
        return "answer_text_mismatch"
    return None


def validate_sft_sample(sample: dict[str, Any], gold_answer: str) -> str | None:
    output = sample["output"]
    required_tags = ("<think>", "</think>", "<answer>", "</answer>")
    if any(tag not in output for tag in required_tags):
        return "missing_required_tag"
    if output.count("<answer>") != 1 or output.count("</answer>") != 1:
        return "invalid_answer_tag_count"
    if extract_answer_tag(output) != gold_answer:
        return "answer_tag_mismatch"
    if len(output) < 80:
        return "output_too_short"
    if len(re.findall(r"\bStep\s+\d+\s*:", output)) < 3:
        return "too_few_steps"
    return None


def convert_sample(sample: dict[str, Any]) -> tuple[dict[str, Any] | None, str | None]:
    reason = validate_processed_sample(sample)
    if reason:
        return None, reason

    sft_sample = {
        "id": sample.get("id", ""),
        "source": sample.get("source", ""),
        "split": sample.get("split", ""),
        "instruction": INSTRUCTION,
        "input": format_input(sample),
        "output": build_output(sample),
    }

    reason = validate_sft_sample(sft_sample, sample["answer"])
    if reason:
        return None, reason

    return sft_sample, None


def build_split(
    paths: list[Path],
    max_samples: int,
    seed: int,
) -> tuple[list[dict[str, Any]], Counter[str], Counter[str], Counter[str]]:
    converted: list[dict[str, Any]] = []
    source_counts: Counter[str] = Counter()
    explanation_counts: Counter[str] = Counter()
    filtered_reasons: Counter[str] = Counter()

    for path in paths:
        for sample in read_jsonl(path, max_samples):
            converted_sample, reason = convert_sample(sample)
            if converted_sample is None:
                filtered_reasons[reason or "unknown"] += 1
                continue

            converted.append(converted_sample)
            source_counts[clean_text(sample.get("source")) or "unknown"] += 1
            if clean_text(sample.get("explanation")):
                explanation_counts["with_explanation"] += 1
            else:
                explanation_counts["without_explanation"] += 1

    rng = random.Random(seed)
    rng.shuffle(converted)
    return converted, source_counts, explanation_counts, filtered_reasons


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        for row in rows:
            file.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_stats(
    stats_path: Path,
    train_rows: list[dict[str, Any]],
    dev_rows: list[dict[str, Any]],
    source_counts: Counter[str],
    explanation_counts: Counter[str],
    filtered_reasons: Counter[str],
    max_samples: int,
    seed: int,
) -> None:
    stats_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# SFT 数据构造统计",
        "",
        f"- seed：`{seed}`",
        f"- max_samples：`{max_samples}`",
        "",
        "## 样本数",
        "",
        f"- train：{len(train_rows)}",
        f"- dev：{len(dev_rows)}",
        "",
        "## Explanation 统计",
        "",
    ]
    for key, count in explanation_counts.most_common():
        lines.append(f"- {key}：{count}")

    lines.extend(["", "## Source 分布", ""])
    for source, count in source_counts.most_common():
        lines.append(f"- {source}：{count}")

    lines.extend(["", "## 过滤原因", ""])
    if filtered_reasons:
        for reason, count in filtered_reasons.most_common():
            lines.append(f"- {reason}：{count}")
    else:
        lines.append("- 无")

    stats_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def build_sft_data(args: argparse.Namespace) -> None:
    train_paths = parse_file_args(args.train_files, args.input_dir) or default_files(
        args.input_dir, args.sources, "train"
    )
    dev_paths = parse_file_args(args.dev_files, args.input_dir) or default_files(
        args.input_dir, args.sources, "dev"
    )

    train_rows, train_sources, train_expl, train_filtered = build_split(
        train_paths, args.max_samples, args.seed
    )
    dev_rows, dev_sources, dev_expl, dev_filtered = build_split(
        dev_paths, args.max_samples, args.seed + 1
    )

    source_counts = train_sources + dev_sources
    explanation_counts = train_expl + dev_expl
    filtered_reasons = train_filtered + dev_filtered

    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl(args.output_dir / "medqa_medmcqa_cot_sft_train.jsonl", train_rows)
    write_jsonl(args.output_dir / "medqa_medmcqa_cot_sft_dev.jsonl", dev_rows)
    write_jsonl(args.output_dir / "preview_20.jsonl", (train_rows + dev_rows)[:20])
    write_stats(
        stats_path=args.stats_path,
        train_rows=train_rows,
        dev_rows=dev_rows,
        source_counts=source_counts,
        explanation_counts=explanation_counts,
        filtered_reasons=filtered_reasons,
        max_samples=args.max_samples,
        seed=args.seed,
    )

    print(f"SFT train: {len(train_rows)}")
    print(f"SFT dev: {len(dev_rows)}")
    print(f"SFT data written to: {args.output_dir}")
    print(f"SFT stats written to: {args.stats_path}")


def main() -> None:
    args = parse_args()
    try:
        build_sft_data(args)
    except KeyboardInterrupt:
        raise
    except Exception as exc:
        print(f"[build_sft_data] failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
